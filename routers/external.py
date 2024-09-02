from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Response, Body, Query, Depends, HTTPException

from .. import schemas, CRUD
from ..db_conf import get_db_session

router = APIRouter(prefix='/external')

# Create for external entities

# Task
@router.post('/task', summary='Add task')
async def create(
    name: str,
    quest_id: str,
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Create a new task
    '''
    task = schemas.Task(name=name, quest_id=quest_id)
    return await CRUD.external.create_task(db=SessionLocal, task=task)


'''Параметры для создания квеста по порядку - содать таск студента
- но для жтого создание таска поправить
159f6327-d09c-4813-b35f-75b69158667d
20f3c702-042f-49a3-950d-0edad1f09c5a
6c2f711e-8071-49c2-a9f3-de425bab23c0
2024-08-28T17:29:20


сессия f3014d47-4286-40c8-8064-5302a2b471b5
'''


# StudentQuest
@router.post('/StudentQuest', summary='Add StudentQuest | start quest session')
async def create(
    quest_id: str,
    group_id: str,
    student_id: str,
    end_at: Optional[str],
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Create a new StudentQuest - quest session
    '''
    stud_q = schemas.StudentQuest(quest_id=quest_id, group_id=group_id, student_id=student_id, end_at=end_at)
    return await CRUD.external.create_student_quest(db=SessionLocal, stud_q=stud_q)


# StudentTask
@router.post('/StudentTask', summary='Add answer to a task')
async def create(
    group_id: str,
    student_id: str,
    quest_id: str,
    student_quest_id: str,
    task_id: str,
    answer: bool,
    SessionLocal: Session = Depends(get_db_session) # connect to DB
):
    '''                       (Docs)
      Add answer to a task (for given student in his quest session)
    '''
    # TODO: mb wrap these params into pydetic object
    stud_t = schemas.StudentTask(group_id=group_id, 
                                 student_id=student_id, 
                                 quest_id=quest_id, 
                                 student_quest_id=student_quest_id, 
                                 task_id=task_id,
                                 answer=answer) 
    return await CRUD.external.create_student_task(db=SessionLocal, stud_t=stud_t)
