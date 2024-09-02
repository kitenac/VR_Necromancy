'''
 cool admin-page - eazy CRUD through db
 [Warning] inteded to be used with non-frontend-accessable entities: 
    - Task/Quest, 
    - StudentTask/StudentQuest 

 ex of problem: Students and Groups are better be CRUDed natively - via frontend (some logic like updating students_count - not implemented by admin_page built-in behaivour) | [design-note] though i can bind my backed`s methods to handle it - it`s still not needed - this way i also should exlude individualy from ModelView for Group and Student soooo much poles - why? if just use frontend?)
        
'''
from sqladmin import Admin, ModelView
# docs: https://aminalaee.dev/sqladmin/configurations/

import logging
from .db_conf import engine, sessionFactory
from .patch_admin_lib import patch_datetime 

patch_datetime() # patching sqladmin to fix render failure of datetime


# ====[START]==== Config models to be displayed at admin page ====[START]====
from .models import (
    Student,
    Group,
    Quest,
    Task,
    StudentQuest,
    StudentTask
) 

# aliasing multiple imports doesn`t works :( - so do it manually(`
models = (
    Student,
    Group,
    Quest,
    Task,
    StudentQuest,
    StudentTask
) 
# ====[END]==== Config models to be displayed at admin page ====[END]====



def create_admin_page(app):
    '''
        Creating app with admin page avaliable at 
        API_URL/admin

        usage: 
            admin = create_admin_page(vr_app)
            admin.mount_to(app=vr_app)
    
        TODO: auth
    '''
    
    admin = Admin(app, engine=engine, session_maker=sessionFactory, title=f"Admin page | {app.title}")
    
    def gen_ModelView(model):
        '''
        Create view-class for sqladmin dynamically by given model
        '''
        class Model_view(ModelView, model=model):
            column_list = [getattr(model, column) for column in model.__dict__ if not column.startswith('_')]
            form_columns = column_list
        return Model_view

    for model in models:        
        admin.add_view(gen_ModelView(model)) 
    
    return admin