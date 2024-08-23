from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Response, Body, Query, Depends, HTTPException

from .. import schemas, CRUD
from ..db_conf import get_db_session

router = APIRouter(prefix='/quests')

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
    return await CRUD.search_quests(SessionLocal, params=params, filter=filter)