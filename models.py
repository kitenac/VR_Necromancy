'''
model - ORM - объект реально связанный с БД (object related model)
'''

from sqlalchemy import Column, ForeignKey, Integer, CHAR, VARCHAR, DATETIME, BOOLEAN, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import declared_attr, relationship  # high level data access for related tables
import uuid


Base = declarative_base()

# common ploes for each class - AUTOGENERATED poles
class CommonModel(Base):
    __abstract__ = True # Class will not create table - just tamplate for other tables
    id         = Column(CHAR(36), default=uuid.uuid4, primary_key=True)
    created_at = Column(TIMESTAMP, default=func.now()) # func - use some sql-function from database   
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

class Group(CommonModel):
    __tablename__ = 'Group'
    name           = Column(CHAR(32), nullable=False)
    students_count = Column(Integer, default=0)
    email          = Column(VARCHAR(128))
    def __str__(self):
        return self.name

    # manage child (btw student also has children wich`ll create cascade deletion`)
    student = relationship('Student', back_populates='group', cascade='all, delete-orphan')

class Student(CommonModel):
    __tablename__ = 'Student'
    group_id  = Column(CHAR(36), ForeignKey('Group.id')) 
    full_name = Column(CHAR(128), nullable=False)

    # for admin page: related poles`re avaliable not in every scenario 
    def __str__(self):
        try: 
            return f'{self.full_name} | {self.group.name}'
        except:    
            return self.full_name
    
    # High level abstraction to easy data accessing
    # now Group of student (same group_id) accessed directly from this pole (when accessing - makes sql query)
    group = relationship('Group', back_populates='student') 
    
    # CHILD-management - enforce cascade deletion - all student`s child entities
    student_quest = relationship('StudentQuest', 
                            back_populates='student', 
                            cascade='all, delete-orphan')
    student_task  = relationship('StudentTask', 
                            back_populates='student', 
                            cascade='all, delete-orphan')


class Quest(CommonModel):
    __tablename__ = 'Quest'
    name = Column(CHAR(128))
    def __str__(self):
        return self.name

class Task(CommonModel):
    __tablename__ = 'Task'
    name     = Column(CHAR(128), nullable=False)
    quest_id = Column(CHAR(36), ForeignKey('Quest.id'))
    def __str__(self):
        try:
            return f'{self.name} | {self.quest.name}'
        except:
            return self.name
    
    quest = relationship('Quest') # for admin page - to select quest => id 


class CommonFK(Base):
    __abstract__ = True
    quest_id   = Column(CHAR(36), ForeignKey('Quest.id')) 
    group_id   = Column(CHAR(36), ForeignKey('Group.id'))
    student_id = Column(CHAR(36), ForeignKey('Student.id'))

# Quest session for student - each student has own Quest context (starts and ends at different time)
class StudentQuest(CommonModel, CommonFK):
    __tablename__ = 'StudentQuest'
    start_at   = Column(TIMESTAMP, default=func.now())
    end_at     = Column(TIMESTAMP, default=None)
    def __str__(self):
        try:
            return f'{self.quest.name} session of student: {self.student.full_name}'
        # in view mode after creation "relationshiped" poles aren`t avaliable:
        except:
            return f'id: {self.id}'
    '''
    When using Foreign keys - it`s needed to specify parent table as relationship
    - needed for proper work of sqladmin 
    - due foreign keys aren`t accessable while create or redo, but relationships persists to select entity (ex: group) on create/redo, so the related keys are automaticaly changed
    '''
    quest = relationship('Quest')
    group = relationship('Group')
    student = relationship('Student')


# particular Task result in Quest session of particular Student
class StudentTask(CommonModel, CommonFK):
    __tablename__ = 'StudentTask'
    answered_at      = Column(TIMESTAMP, default=func.now())
    answer           = Column(BOOLEAN)
    def __str__(self):
        return 'student_quest_id: ' + self.student_quest_id
    
    task_id          = Column(CHAR(36), ForeignKey('Task.id'))
    student_quest_id = Column(CHAR(36), ForeignKey('StudentQuest.id'))     # quest-session id

    # needed for proper work of sqladmin with foreign keys above    
    quest         = relationship('Quest')
    group         = relationship('Group')
    student       = relationship('Student')
    task          = relationship('Task')
    student_quest = relationship('StudentQuest')