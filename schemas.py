'''
schema - схема данных
- таблицы
- запросы/ответы
- ...
'''

from pydantic import BaseModel, Field # easy converting data to JSON, validating types
from typing import Dict, List, Optional # annotations for dictionaries


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
class Group(BaseModel):
  id: str
  name: str
  students_count: int
  email: str

  # add support for orm`s objects - by poles (in pydentic - by keys):
  #   in orm:      id = data.id
  #   in pydentic: id = data['id']  
  class Config:
     from_attributes = True
  
class Student(BaseModel):
  id: str
  group_id: str
  full_name: str
  class Config:
     from_attributes = True


# ==== HTTP methods data schemas
class PUT_Student(BaseModel):
  full_name: str
  class Config:
     from_attributes = True  

class PUT_Group(BaseModel):
  # only one pole required => both params`re optional in a way)
  name:  Optional[str] = None
  email: Optional[str] = None
  class Config:
     from_attributes = True