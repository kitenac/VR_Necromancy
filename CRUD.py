'''
Core for HTTP methods` handlers (from main)
- bd operations
- forming request body
- raising HTTP exceptions (codes) 
'''

from fastapi import HTTPException
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.selectable import Select  # annotation for async transaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func

from typing import List, Optional
import logging

from db_conf import get_db_session  # session to our DB
import models                       # existing tables
import schemas                      # data schemas


def prepare_params(
        params: schemas.RequestQuery,  
        model: object
    ):
    '''
    prepare params from client to pagination and filtering
        query url params:       
            limit: 10,
            page: 1,
            order: ['-name']
    '''
    
    def get_order(column: str):
        '''
        Getting order (column-object for sqlalchemy query.order_by()
        column:  asc: name | desc: -name
        order:   expected to be an object - column of table(model),
                    e.g. order = Student.full_name
        '''
        # Truncate leading '-' and set DESC mod if need
        ASC = True  # ascending sorting
        if column[0] == '-':
            ASC = False
            column = column[1:len(column)]

        # validate if column from request persists in table and apply sorting in ASC or DESC
        order = column in model.__table__.columns.keys() 
        if order: 
            if ASC:
                return model.__dict__[column]
            else:
                return desc(model.__dict__[column])
        else:
            return False # no sorting required

    column = params.order[0] # пока только по одному столбцу (первому) - ограничения frontend
    skip = (params.page - 1) * params.limit  # -1 - due index shift (frontend counts pages from 1, not from 0)

    return skip, get_order(column)

# TODO: 
# - decompose searching and pagination + oredering logic
# - create schema for function parametrs      
async def search_and_pag(
        db: AsyncSession,   
        query_all: Select,  # select where to search, ex: db.query(models.Group)
        params: schemas.RequestQuery, 
        filter: Optional[List[schemas.RequestBody.FilterItem]],
        model: object  # e.g., models.Student
    ):
    '''
    Searching, pagination + ordering
    '''

    skip, order = prepare_params(params, model)

    # Search
    if filter:
        # Taking only the 0-th filter's element, as the frontend doesn't take greater
        search, search_col = filter[0].value, filter[0].column  
        if search and (search_col in model.__table__.columns.keys()):
            query_all = query_all.where(getattr(model, search_col).ilike(f"{search}"))

    # Unsliced pages query for counting
    unsliced_pages_query = query_all

    # Sorting - must be called before slicing
    if order is not False:  # Ensure order is not False
        query_all = query_all.order_by(order)

    # Pagination - slicing
    query_page = query_all.offset(skip).limit(params.limit)

    # Execute the queries asynchronously
    all_students = select(func.count()).select_from(unsliced_pages_query)
    total_count = await db.execute(all_students)  # Get the total count of filtered elements
    page = await db.execute(query_page)           # Get the actual model instances
    
    return total_count.scalar(), page.scalars().all()  # Return the total count and the selected page


async def search_groups(   
        db: AsyncSession,  
        params: schemas.RequestQuery, 
        filter: Optional[List[schemas.RequestBody.FilterItem]]
    ):
    
    query_all = select(models.Group)
    total, data = await search_and_pag(
        db=db,
        query_all=query_all,
        params=params,
        filter=filter,
        model=models.Group
    )

    
    return  schemas.API_Response( 
        data = [schemas.Group(name=row.name, email=row.email, id=row.id, students_count=row.students_count) for row in data],
        meta = schemas.API_Response.MetaData(total=total)
        )


async def search_students(
        db: AsyncSession, 
        group_id: str, 
        params: schemas.RequestQuery, 
        filter: Optional[List[schemas.RequestBody.FilterItem]]
    ):
     
    query_all = select(models.Student).where(models.Student.group_id == group_id)  # query to select all students of group
    total, data = await search_and_pag(
        db=db,
        query_all=query_all,
        params=params,
        filter=filter,
        model=models.Student
    )

    # TODO: somehow automate data below
    return  schemas.API_Response( 
        data = [schemas.Student(full_name=row.full_name, id=row.id, group_id=row.group_id) for row in data],
        meta = schemas.API_Response.MetaData(total=total)
        )



async def create(db: AsyncSession, el: object):
    '''
    Inserting rows one at a time - can be inefficient. 
    Batching multiple inserts into a single transaction can reduce the time. 
    - instead of inserting each row individually, you can insert multiple rows in one command
    
    TODO: Оптимизация (при ооочень большом числе rps) - просто транзакцию возвращать, а commit() по таймингу делать, когда их много накопится 
    - для этого celery должен подойти по идее 
    '''
    db.add(el)  
    await db.commit() # write to db
    await db.refresh(el) # fetch auto-generated fileds from db (like timestamp)
    
    return el    



async def create_group(db: AsyncSession, group: schemas.Group):
    # unpacking group 
    #   not to spaggetting: id = group.id, name=group.name, email=group.email, students_count=group.students_count
    db_group = models.Group(**group.model_dump())
    return await create(db, el=db_group)


async def create_student(db: AsyncSession, student: schemas.Student):
    async with db.begin():  # Ensure we're in an async context
        db_student = models.Student(**student.model_dump())
        res = await create(db, el=db_student)
        
        if res: # wait till async call results
            # handle side effect on Group table
            db_student.group.students_count += 1 # Update | [Explain] access to .groups - is "lazy propagation" - hidden sql query when needed - see models.Student.group
            await db.commit()

            return res



async def delete(db: AsyncSession, del_elements: list[object] = [], id: Optional[str]='not given', maby_empty=False):
    ''' Delete group of elements 

         - returns OK-status or rises HTTPException if need - to be handeled in app (main.py)  
         - id - optional - passed to provide additional info regarding deleting object
         
         - maby_empty - flag to indicate that del_elements CAN be empty list and this will not lead to an HTTP 404 error 
            - example: 
                when deleting a group of students firstly we need to delete all students
                if there`s no students there might be an error - empty list to delete, BUT for deleting group that`s OK and doesn`t affects main operation (deleting group)
    '''
    
    if None not in del_elements: # empty list of elements to delete | filter returns None if nothing found
        for el_del in del_elements:
            db.delete(el_del)      # gather in query all items to delete 
        
        await db.commit() # execute deletion
        return f'Successfully deleted {id}' # status
    
    elif not maby_empty:
        raise HTTPException(status_code=404, detail=f'There`s no el with such id = {id}') # pass to exception handler in main


async def delete_student(db: AsyncSession, id: str):
    student = await db.query(models.Student).filter(models.Student.id == id).first() 
    group = await student.group # save group before student will be deleted bellow => info about it`s group`ll unavalible 
    res = await delete(db=db, id=id, del_elements=[student])

    # Update ammount of students in group after successfull deletion (failed deletion - turns execuion into exception-handling and doesn`t reach here)
    group.students_count -= 1 
    await db.commit()
    return res


async def delete_group(db: AsyncSession, id: str):
    # first - delete all group`s students
    group_students = await db.query(models.Student).filter(models.Student.group_id == id).all()
    await delete(db=db, del_elements=group_students, maby_empty=True)
    
    # only than delete the group (logical + constraint of PK-chainig group_id with students will not allow deletion otherwise)
    group = await db.query(models.Group).filter(models.Group.id == id).first()
    return await delete(db=db, del_elements=[group], id=id)
    

    
async def redo_group(db: AsyncSession, id: str, redacted_group: schemas.PUT_Group):
    group = await db.query(models.Group).filter(models.Group.id == id).first()

    # redo all not empty poles 
    # TODO: take poles from pydentic model schemas.PUT_Group automatically
    poles = ['name', 'email']
    for pole in poles:
        if redacted_group.__dict__[pole]:
            setattr(group, pole, redacted_group.__dict__[pole]) # set pole by name
            
    await db.commit()



async def redo_student(db: AsyncSession, id: str, redacted_student: schemas.PUT_Student):
    group = await db.query(models.Student).filter(models.Student.id == id).first()

    poles = ['full_name']

    for pole in poles:
        if redacted_student.__dict__[pole]:
            setattr(group, pole, redacted_student.__dict__[pole]) # set pole by name
            
    await db.commit()


if __name__ == '__main__':
    # TODO - session management !!!!!

    # create sessions to our DB
    SessionLocal = get_db_session()

    params = schemas.RequestQuery(limit=10, page=1, order=['-created_at'])
    filter = [ schemas.RequestBody.FilterItem(column='full_name', operator='ilike', value=r'') ]

    #result = search_students(SessionLocal, params=params, filter=filter, group_id='2455ab10-51d7-11ef-bc51-0242ac110003')
    result = search_groups(SessionLocal, params=params, filter=filter)

    for row in result:
        print(f'{row} | {type(row)} | {row.__dict__}')


    '''
    in POST url params:       
            limit: 10,
            page: 1,
            order: ['-name']

        in POST body:
        {
            "with":{
                "relationships":["students"]},
            "filter":[
                {"column":"name",
                "operator":"ilike",
                "value":"%search%"}
            ]
        } 
    '''