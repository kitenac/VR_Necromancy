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

'''
# Quest containing tables^
class Task(BaseModel):
   task_id: str
   task_name: str
   answer: bool
   answered_at: str

class StudentQuest(BaseModel):
    id: str
    student_full_name: str
    quest_start_at: str
    quest_end_at: str
    quest_total_tasks_count: int
    quest_true_answer_count: int
    quest_false_answer_count: int
    tasks: list[Task] # or task_map
    student_id: str
'''

     
# ==== HTTP methods data schemas
class PUT_Student(BaseModel):
  full_name: str

class PUT_Group(BaseModel):
  # only one pole required => both params`re optional in a way)
  name:  Optional[str] = None
  email: Optional[str] = None
