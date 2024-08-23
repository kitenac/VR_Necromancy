from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Response, Body, Query, Depends, HTTPException

from .. import schemas, CRUD
from ..db_conf import get_db_session

router = APIRouter(prefix='/students')

# Create
@router.post('', summary='Add student')
async def student_create(
    full_name: str = Body(),
    group_id: str = Body(),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Create new student 
    '''
    student = schemas.Student(group_id=group_id, full_name=full_name)
    return await CRUD.students.create(db=SessionLocal, student=student)


# Delete
# - errors here goes to HTTPExeption and handler in at very start of main.py 
@router.delete('/{id}', status_code=200, summary='Delete student by id')
async def student_delete(
    id: str,
    SessionLocal: Session = Depends(get_db_session),
    response = Response() # response object of fastapi: headers, status_code and other crusual lays here
):
    '''                   (Docs)
    Delete selected student 
    '''
    status = await CRUD.students.delete(db=SessionLocal, id=id)
    
    return schemas.API_Response(
        status=status,
        code=response.status_code
    )


# ==== Redo
@router.put('/{id}', status_code=200, summary='redo student')
async def student_redo(
  id: str,
  redo_student: schemas.PUT_Student,
  SessionLocal: Session = Depends(get_db_session),
  response = Response()
):
    '''
    Redo selected student by fullname
    '''

    if not redo_student.full_name:
        raise HTTPException(status_code=400, detail='Bad request: full_name must be specified')

    await CRUD.students.redo(db=SessionLocal, id=id, redacted_student=redo_student)
    return schemas.API_Response(
        status='Successfully redacted student',
        code=response.status_code
    )


# Search: pagination + filtering + sorting
@router.post('/search', summary='View students of group')
async def student_search(
    request: Request,  # client_url can be retrived from Header "Referer"
    filter: Optional[List[schemas.RequestBody.FilterItem]] = None,  # Body parameter
    with_aliased: Optional[schemas.RequestBody.With] = Body(default=None, alias="with"),  # Use Body to extract 'with' directly
    limit: int = 10,
    page: int = 1,
    order: list[str] = Query(['id'], alias='order[]'),
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Get all students of chosen group,
      - pagination + filtering + sorting
    '''
    
    client_url = request.headers.get('referer') #  from Header "Referer"
    group_id = client_url.split('/')[-1] # last arg of client`s url is group id
    params = schemas.RequestQuery(limit=limit, page=page, order=order)
    
    return await CRUD.students.search(SessionLocal, params=params, filter=filter, group_id=group_id)