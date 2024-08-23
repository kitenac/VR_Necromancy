# Module imports
from .. import schemas
from .. import models
from .core.search import search_and_pag 
from .core.create import create_core

# Libs
from sqlalchemy.orm import Session
from typing import Optional, List


# Can be called from auto-doc page
async def create(db: Session, quest: schemas.Quest):
    db_quest = models.Quest(**quest.model_dump())
    return await create_core(db, el=db_quest)


async def search(   
        db: Session,  
        params: schemas.Quest, 
        filter: Optional[List[schemas.RequestBody.FilterItem]]
    ):
     
    query_all = db.query(models.Quest)
    total, data = await search_and_pag(
        query_all=query_all,
        params=params,
        filter=filter,
        model=models.Quest
    )
    
    return  schemas.API_Response( 
        data = [schemas.Quest(**row.__dict__) for row in data],
        meta = schemas.API_Response.MetaData(total=total)
        )

