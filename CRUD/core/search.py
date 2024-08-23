'''
Core for HTTP methods` handlers (from main)
- bd operations
- forming request body
- raising HTTP exceptions (codes) 
'''

from sqlalchemy import desc
from sqlalchemy.orm import Query

from typing import List, Optional
import logging

from ...db_conf import get_db_session  # session to our DB
from ... import schemas                # data schemas



def prepare_params(
        params: schemas.RequestQuery,  
        model: object
    ):
    '''
    prepare params from client to pagination and filtering
        query url params:       
            limit: 10,
            page: 1,
            order: ['-name']
    '''
    
    def get_order(column: str):
        '''
        Getting order (column-object for sqlalchemy query.order_by()
        column:  asc: name | desc: -name
        order:   expected to be an object - column of table(model),
                    e.g. order = Student.full_name
        '''
        # Truncate leading '-' and set DESC mod if need
        ASC = True  # ascending sorting
        if column[0] == '-':
            ASC = False
            column = column[1:len(column)]

        # validate if column from request persists in table and apply sorting in ASC or DESC
        order = column in model.__table__.columns.keys() 
        if order: 
            if ASC:
                return model.__dict__[column]
            else:
                return desc(model.__dict__[column])
        else:
            return False # no sorting required

    column = params.order[0] # пока только по одному столбцу (первому) - ограничения frontend
    skip = (params.page - 1) * params.limit  # -1 - due index shift (frontend counts pages from 1, not from 0)

    return skip, get_order(column)

# TODO: 
# - decompose searching and pagination + oredering logic
# - create schema for function parametrs
async def search_and_pag(
        query_all: Query, # select where to search, ex: db.query(models.Group)
        params: schemas.RequestQuery, 
        filter: Optional[List[schemas.RequestBody.FilterItem]],
        model: object # ex: models.Student
    ):
    '''
    Searaching, pagination + ordering
     - to be decomposed in 2 parts 'soon'
    '''

    skip, order = prepare_params(params, model)
    #logging.info(f'order: {order} | {str(order)}')

    # search
    if filter:
        # Taking only 0-th filter`s element, due frontend doesn`t takes greater
        search, search_col = filter[0].value, filter[0].column  
        if search and (search_col in model.__table__.columns.keys()):
            query_all = query_all.filter(model.__dict__[search_col].ilike(search))   

    # pagination
    '''fix query to know ammount of elements before pagination=slicing + before ordering - no needed to know ammount of els'''
    unsliced_pages_query = query_all # NOTE: deepcopy() doesn`t works with query, but 'native' coping works fine - by value

    # sorting - must be called before slicing (group by must be before limit amd offset)
    if not order == False:  # NOTE: 'if order' gives error (bool isn`t defined for order:UnaryExpression)
        query_all = query_all.order_by(order)

    # pagination - slicing
    query_page = query_all.offset(skip).limit(params.limit)

    return len(unsliced_pages_query.all()), query_page.all()   # ammount of filtered elements and selected page



'''
    in POST url params:       
            limit: 10,
            page: 1,
            order: ['-name']

        in POST body:
        {
            "with":{
                "relationships":["students"]},
            "filter":[
                {"column":"name",
                "operator":"ilike",
                "value":"%search%"}
            ]
        } 
'''