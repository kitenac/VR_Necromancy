# Module imports
from .. import schemas
from .. import models
from .core.search import search_and_pag 
from .core.create import create_core
from .core.delete import delete_core
from .core.redo   import redo_core

# Libs
from sqlalchemy.orm import Session
from typing import Optional, List


async def create(db: Session, student: schemas.Student):
    db_student = models.Student(**student.model_dump())
    res = await create_core(db, el=db_student)
    
    # handle side effect on Group table
    db_student.group.students_count += 1 # Update | [Explain] access to .groups - is "lazy propagation" - hidden sql query when needed - see models.Student.group
    db.commit()  # Commit the changes to db
    return res

async def delete(db: Session, id: str):
    student = db.query(models.Student).filter(models.Student.id == id).first() 
    group = student.group # save group before student will be deleted bellow => info about it`s group`ll unavalible 
    res = await delete_core(db=db, id=id, del_elements=[student])

    # Update ammount of students in group after successfull deletion (failed deletion - turns execuion into exception-handling and doesn`t reach here)
    group.students_count -= 1 
    db.commit()
    return res

async def redo(db: Session, id: str, redacted_student: schemas.PUT_Student):
    await redo_core(db=db, 
               id=id, 
               redacted_schema=redacted_student, 
               redo_model=models.Student)

async def search(
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

    return  schemas.API_Response( 
        data = [schemas.Student(**row.__dict__) for row in data],
        meta = schemas.API_Response.MetaData(total=total)
        )