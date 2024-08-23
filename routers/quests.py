from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Response, Body, Query, Depends, HTTPException

from .. import schemas, CRUD
from ..db_conf import get_db_session

router = APIRouter(prefix='/quests')

# Create
@router.post('', summary='Add quest')
async def quest_create(
    name: str = Body(),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Create a new quest
    '''
    quest = schemas.Quest(name=name)
    return await CRUD.quests.create(db=SessionLocal, quest=quest)


@router.post('/search', summary='View avaliable quests')
async def quests_search(
    request: Request,  # client_url can be retrived from Header "Referer"
    filter: Optional[List[schemas.RequestBody.FilterItem]] = None,  # Body parameter
    with_aliased: Optional[schemas.RequestBody.With] = Body(default=None, alias="with"),  # Use Body to extract 'with' directly
    limit: int = 10,
    page: int = 1,
    order: list[str] = Query(['id'], alias='order[]'),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Get all excisting quests,
      - pagination + filtering + sorting
    '''
    params = schemas.RequestQuery(limit=limit, page=page, order=order)
    return await CRUD.quests.search(SessionLocal, params=params, filter=filter)
