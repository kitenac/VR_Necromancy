'''
schema - схема данных
- таблицы
- запросы/ответы
- ...
'''

from pydantic import BaseModel, Field # easy converting data to JSON, validating types
from typing import Dict, List, Optional # annotations for dictionaries
from datetime import datetime
from sqlalchemy import func


# ======= Response =======
# API response template
class API_Response(BaseModel):
    class MetaData(BaseModel):
       total: int = 10
       TODO: str = 'mb some other params needed here'

    # actual data from Data base:
    data: list[object] = []
    # mandatory for client (for pagination)
    meta: MetaData = MetaData() 
    # some request info:
    status: str = 'not implemented'
    code: int = 0             
  


# ======= Request =======
# class - collection of request`s body params` schemas 
class RequestBody:
  
  # for item inside filter parametr
  class FilterItem(BaseModel):
      column: str
      operator: Optional[str] = ''
      value: str             # already has ~regex for like:  %search_val%

  # with param is object - not itter like abowe and can be defined fully
  class With(BaseModel):
      with_: Optional[Dict[str, List[str]]] = Field(default=None, alias="with"),  # call 'with_' as 'with' by Field - to avoid keyword conflict 

  # request options
  filter: Optional[List[FilterItem]] = None
  with_: Optional[Dict[str, List[str]]] = Field(default=None, alias="with") # call 'with_' as 'with' by Field - to avoid keyword conflict

# query params from url
class RequestQuery(BaseModel):
  limit: int
  page: int
  order: List[str] = None




# ======= Tables =======

# common poles for each table
class CommonTable(BaseModel):
   # auto generated poles - so make `em optional (by None)
   id: Optional[str] = None
   created_at: Optional[datetime] =  None
   updated_at: Optional[datetime] =  None
  
   # add support for orm`s objects - by poles (in pydentic - by keys):
   #   in orm:      id = data.id
   #   in pydentic: id = data['id']  
   class Config:
     from_attributes = True


class Group(CommonTable):
  name: str
  email: str
  students_count: Optional[int] = 0
  
class Student(CommonTable):
  group_id: str
  full_name: str

# Tables for Quest`s Page
class Quest(CommonTable):
   name: str


# Each Quest contains tasks:
class Task(CommonTable):
    name: str
    quest_id: str

# Common Foreign Keys 
class CommonFK(BaseModel):
  quest_id: str
  group_id: str
  student_id: str

# Quest session for student - each student has own Quest context (starts and ends at different time)
class StudentQuest(CommonTable, CommonFK):
  start_at: Optional[datetime] = None
  end_at: Optional[datetime] = None

# particular Task result in Quest session of particular Student
class StudentTask(CommonTable, CommonFK):
  student_quest_id: str
  task_id: str
  answer: bool
  answered_at: Optional[datetime] = None


# === Syntetic data schema for API-response, 
# not real table, but an agregation of StudentQuests & StudentTasks

# view of task for API response
class TaskView(BaseModel):
   task_id: str
   task_name: str
   answer: bool
   answered_at: datetime  

# view of particular Student`s progress on Quest - array of this items - is progress of group
# all params are optional - bc they`re counting in few steps
class StudentProgress(BaseModel):
    student_id: str         = None
    student_full_name: str  = None 
    quest_start_at: Optional[datetime] = None
    quest_end_at:     Optional[datetime] = None
    quest_total_tasks_count: int  = None
    quest_true_answer_count: int  = None
    quest_false_answer_count: int = None
    tasks: list[TaskView] = None

     
# ==== HTTP methods data schemas
class PUT_Student(BaseModel):
  full_name: str

class PUT_Group(BaseModel):
  # only one pole required => both params`re optional in a way)
  name:  Optional[str] = None
  email: Optional[str] = None
