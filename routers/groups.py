from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Response, Body, Query, Depends, HTTPException

from .. import schemas, CRUD
from ..db_conf import get_db_session


router = APIRouter(prefix='/groups')

# Search: pagination + filtering + sorting
@router.post('/search', summary='View groups')
async def groups_search(
    request: Request,  # client_url - fastapi handles
    filter: Optional[List[schemas.RequestBody.FilterItem]] = None,  # Body parameter
    with_aliased: Optional[schemas.RequestBody.With] = Body(default=None, alias="with"),  # Use Body to extract 'with' directly
    limit: int = 10,
    page: int = 1,
    order: list[str] = Query(['id'], alias='order[]'),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
  ):
    '''                       (Docs)
      Get all groups
      - pagination + filtering + sorting
    '''
    
    params = schemas.RequestQuery(limit=limit, page=page, order=order)
    return await CRUD.search_groups(SessionLocal, params=params, filter=filter)

# Create
@router.post('/', summary='Add group')
async def students_create(
    name: str = Body(),
    email: str = Body(),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Create a new group 
    '''
    group = schemas.Group(name=name, email=email)
    return await CRUD.create_group(db=SessionLocal, group=group)


# Delete
# - errors here goes to HTTPExeption and handler in at very start of main.py 
@router.delete('/{id}', status_code=200, summary='Delete group by id')
async def group_delete(
    id: str,
    SessionLocal: Session = Depends(get_db_session),
    response = Response() # response object of fastapi: headers, status_code and other crusual lays here
):
    '''                   (Docs)
    Delete selected group 
    '''
    status = await CRUD.delete_group(db=SessionLocal, id=id)
    
    return schemas.API_Response(
        status=status,
        code=response.status_code
    )


# ==== Redo
@router.put('/{id}', status_code=200, summary='redo group')
async def group_redo(
  id: str,
  redo_group: schemas.PUT_Group,
  SessionLocal: Session = Depends(get_db_session),
  response = Response()
):
    '''
    Redo selected group by email/name/both
    '''

    if not redo_group.name and not redo_group.email:
        raise HTTPException(status_code=400, detail='Bad request: either name or email must be specified')

    await CRUD.redo_group(db=SessionLocal, id=id, redacted_group=redo_group)
    return schemas.API_Response(
        status='Successfully redacted group',
        code=response.status_code
    )