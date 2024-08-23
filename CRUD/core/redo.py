from pydantic import BaseModel # for annotating schemas
from sqlalchemy.orm import Session


async def redo_core(db: Session, id: str, redacted_schema: BaseModel, redo_model: object):
    old_el = db.query(redo_model).filter(redo_model.id == id).first()
    redo_el_dict = redacted_schema.model_dump() # get dictionary from redo element
    
    for key, val in redo_el_dict.items():
        if val:
            setattr(old_el, key, val) # set pole by name
            
    db.commit()