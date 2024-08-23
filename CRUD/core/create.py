from sqlalchemy.orm import Session

'''
TODO: Оптимизация (при ооочень большом числе rps) - просто транзакцию возвращать, а commit() по таймингу делать, когда их много накопится 
- для этого celery должен подойти по идее 
    
inserting rows one at a time - can be inefficient. 
Batching multiple inserts into a single transaction can reduce the time. 
- instead of inserting each row individually, you can insert multiple rows in one command
'''
async def create_core(db: Session, el: object):
    db.add(el)  
    db.commit() # write to db
    db.refresh(el) # fetch auto-generated fileds from db (like timestamp)
    return el    