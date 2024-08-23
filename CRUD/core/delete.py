from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional

async def delete_core(db: Session, del_elements: list[object] = [], id: Optional[str]='not given', maby_empty=False):
    ''' Delete group of elements 

         - returns OK-status or rises HTTPException if need - to be handeled in app (main.py)  
         - id - optional - passed to provide additional info regarding deleting object
         
         - maby_empty - flag to indicate that del_elements CAN be empty list and this will not lead to an HTTP 404 error 
            - example: 
                when deleting a group of students firstly we need to delete all students
                if there`s no students there might be an error - empty list to delete, BUT for deleting group that`s OK and doesn`t affects main operation (deleting group)
    '''
    
    if None not in del_elements: # empty list of elements to delete | filter returns None if nothing found
        for el_del in del_elements:
            db.delete(el_del)      # gather in query all items to delete 
        
        db.commit() # execute deletion
        return f'Successfully deleted {id}' # status
    
    elif not maby_empty:
        raise HTTPException(status_code=404, detail=f'There`s no el with such id = {id}') # pass to exception handler in main