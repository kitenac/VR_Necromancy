from .. import schemas
from .. import models

from .core.create import create_core

# Libs
from sqlalchemy.orm import Session

'''
 Create external entities
 - mock-like
 UPD - use /admin page to CRUD via external entities
'''

# === Create methods

# Task
async def create_task(db: Session, task: schemas.Task):
    db_task = models.Task(**task.model_dump())
    return await create_core(db, el=db_task)

async def create_student_quest(db: Session, stud_q: schemas.StudentQuest):
    db_stud_q = models.StudentQuest(**stud_q.model_dump())
    return await create_core(db, el=db_stud_q)

async def create_student_task(db: Session, stud_t: schemas.StudentQuest):
    db_stud_t = models.StudentTask(**stud_t.model_dump())
    return await create_core(db, el=db_stud_t)