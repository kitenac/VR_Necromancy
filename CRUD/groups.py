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

async def create(db: Session, group: schemas.Group):
    # unpacking group 
    #   not to spaggetting: id = group.id, name=group.name, email=group.email, students_count=group.students_count
    db_group = models.Group(**group.model_dump())
    return await create_core(db, el=db_group)

async def delete(db: Session, id: str):
    group = db.query(models.Group).filter(models.Group.id == id).first()
    return await delete_core(db=db, del_elements=[group], id=id)


# [Discuss] function redo_* below not really necessory (.core.redo allready has all needed),
#  but for better readability/flexability it`s good to have such function 
async def redo(db: Session, id: str, redacted_group: schemas.PUT_Group):
    await redo_core(db=db, 
               id=id, 
               redacted_schema=redacted_group, 
               redo_model=models.Group)


async def search(   
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
        data = [schemas.Group(**row.__dict__) for row in data], # unpack dictionary of models` key to initialize schema
        meta = schemas.API_Response.MetaData(total=total)
        )