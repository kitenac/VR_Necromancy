from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db_conf import get_db_session
from .. import CRUD

router = APIRouter(prefix='/progress')


@router.get('/get', summary='get quest`s progress for group')
async def read(
    group_id: str,
    quest_id: str,
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):    
    '''
    Get progress of chosen group for some quest:
    - i.e. group of tasks for each student of group

    * there`s no pagination, filtering and sorting (left for frontend) - just reading  
    '''
    return await CRUD.progress.read(SessionLocal, group_id=group_id, quest_id=quest_id)