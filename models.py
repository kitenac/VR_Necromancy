'''
model - ORM - объект реально связанный с БД (object related model)
'''

from sqlalchemy import Column, ForeignKey, Integer, CHAR, VARCHAR, DATETIME, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship  # high level data access for related tables

Base = declarative_base()

class Group(Base):
    __tablename__ = 'Group'
    id = Column(CHAR(36), primary_key=True)
    name = Column(CHAR(32), nullable=False)
    students_count = Column(Integer)
    email = Column(VARCHAR(128))


class Student(Base):
    __tablename__ = 'Student'
    id = Column(CHAR(36), primary_key=True)
    group_id = Column(CHAR(36), ForeignKey('Group.id')) 
    full_name = Column(CHAR(128), nullable=False)

    # High level abstraction to easy data accessing
    # now Group of student (same group_id) accessed directly from this pole (when accessing - makes sql query)
    group = relationship('Group') # unidirectional relation as example
    

class Task(Base):
    __tablename__ = 'Task'
    task_id = Column(CHAR(36), primary_key=True)
    task_name = Column(CHAR(32), nullable=False)
    answer = Column(BOOLEAN)
    answered_at = Column(DATETIME)

