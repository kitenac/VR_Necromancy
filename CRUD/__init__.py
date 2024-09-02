''' 
importing module`s files to be accessed directly when import CRUD module
    ex.
        import CRUD
        CRUD.group.create()  # treat group "like sub-module"
'''
from . import groups, students, quests, progress, external