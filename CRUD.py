'''
Core for HTTP methods` handlers (from main)
- bd operations
- forming request body
- raising HTTP exceptions (codes) 
'''

from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker, Query
from sqlalchemy import desc

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
        query_all: Query, # select where to search, ex: db.query(models.Group)
        params: schemas.RequestQuery, 
        filter: Optional[List[schemas.RequestBody.FilterItem]],
        model: object # ex: models.Student
    ):
    '''
    Searaching, pagination + ordering
     - to be decomposed in 2 parts 'soon'
     - ordering doesn`t work
    '''

    skip, order = prepare_params(params, model)
    #logging.info(f'order: {order} | {str(order)}')

    # search
    if filter:
        # Taking only 0-th filter`s element, due frontend doesn`t takes greater
        search, search_col = filter[0].value, filter[0].column  
        if search and (search_col in model.__table__.columns.keys()):
            query_all = query_all.filter(model.__dict__[search_col].ilike(search))   

    # pagination
    '''fix query to know ammount of elements before pagination=slicing + before ordering - no needed to know ammount of els'''
    unsliced_pages_query = query_all # NOTE: deepcopy() doesn`t works with query, but 'native' coping works fine - by value

    # sorting - must be called before slicing (group by must be before limit amd offset)
    if not order == False:  # NOTE: 'if order' gives error (bool isn`t defined for order:UnaryExpression)
        query_all = query_all.order_by(order)

    # pagination - slicing
    query_page = query_all.offset(skip).limit(params.limit)

    return len(unsliced_pages_query.all()), query_page.all()   # ammount of filtered elements and selected page
    
      


async def search_groups(   
        db: Session,  
        params: schemas.RequestQuery, 
        filter: Optional[List[schemas.RequestBody.FilterItem]]
    ):
     
    query_all = db.query(models.Group)
    total, data = await search_and_pag(
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
        db: Session, 
        group_id: str, 
        params: schemas.RequestQuery, 
        filter: Optional[List[schemas.RequestBody.FilterItem]]
    ):
     
    query_all = db.query(models.Student).filter(models.Student.group_id == group_id) # query to select all students of group 
    total, data = await search_and_pag(
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



'''
TODO: Оптимизация (при ооочень большом числе rps) - просто транзакцию возвращать, а commit() по таймингу делать, когда их много накопится 
- для этого celery должен подойти по идее 
    
nserting rows one at a time - can be inefficient. 
Batching multiple inserts into a single transaction can reduce the time. 
- instead of inserting each row individually, you can insert multiple rows in one command
'''
async def create(db: Session, el: object):
    db.add(el)  
    db.commit() # write to db
    db.refresh(el) # fetch auto-generated fileds from db (like timestamp)
    return el    



async def create_group(db: Session, group: schemas.Group):
    # unpacking group 
    #   not to spaggetting: id = group.id, name=group.name, email=group.email, students_count=group.students_count
    db_group = models.Group(**group.model_dump())
    return await create(db, el=db_group)


async def create_student(db: Session, student: schemas.Student):
    db_student = models.Student(**student.model_dump())
    res = await create(db, el=db_student)
    
    # handle side effect on Group table
    db_student.group.students_count += 1 # Update | [Explain] access to .groups - is "lazy propagation" - hidden sql query when needed - see models.Student.group
    db.commit()  # Commit the changes to db
    return res



async def delete(db: Session, del_elements: list[object] = [], id: Optional[str]='not given', maby_empty=False):
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
        
        db.commit() # execute deletion
        return f'Successfully deleted {id}' # status
    
    elif not maby_empty:
        raise HTTPException(status_code=404, detail=f'There`s no el with such id = {id}') # pass to exception handler in main


async def delete_student(db: Session, id: str):
    student = db.query(models.Student).filter(models.Student.id == id).first() 
    group = student.group # save group before student will be deleted bellow => info about it`s group`ll unavalible 
    res = await delete(db=db, id=id, del_elements=[student])

    # Update ammount of students in group after successfull deletion (failed deletion - turns execuion into exception-handling and doesn`t reach here)
    group.students_count -= 1 
    db.commit()
    return res


async def delete_group(db: Session, id: str):
    # first - delete all group`s students
    group_students = db.query(models.Student).filter(models.Student.group_id == id).all()
    await delete(db=db, del_elements=group_students, maby_empty=True)
    
    # only than delete the group (logical + constraint of PK-chainig group_id with students will not allow deletion otherwise)
    group = db.query(models.Group).filter(models.Group.id == id).first()
    return await delete(db=db, del_elements=[group], id=id)
    


async def redo(db: Session, id: str, redacted_schema: object, redo_model: object):
    old_el = db.query(redo_model).filter(redo_model.id == id).first()

    for pole in redacted_schema.__dict__:
        if redacted_schema.__dict__[pole]:
            setattr(old_el, pole, redacted_schema.__dict__[pole]) # set pole by name
            
    db.commit()
    

# [Discuss] functions redo_* below not really necessory (redo allready has all needed), but for better readability/flexability it`s good to have such functions (to much parametrs)
async def redo_group(db: Session, id: str, redacted_group: schemas.PUT_Group):
    await redo(db=db, 
               id=id, 
               redacted_schema=redacted_group, 
               redo_model=models.Group)

async def redo_student(db: Session, id: str, redacted_student: schemas.PUT_Student):
    await redo(db=db, 
               id=id, 
               redacted_schema=redacted_student, 
               redo_model=models.Student)


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