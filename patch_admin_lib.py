''' Patching datetime render (self.data - couldn`t interpretate as - Boolean not implemented for clause...)'''

# importing buggy module  
import wtforms.fields.datetime as BugyLibPart


def patch_date_time_value(self):
    if self.raw_data:
        return " ".join(self.raw_data)    
    # self.data - can`t be booled - so there was problem accessing self.data.strftime
    try:
        return self.data.strftime(self.format[0])
    # set default value 
    except: 
        return 'not specified'
    

def patch_datetime():
    ''' patching sqladmin to fix render failure of datetime '''
    BugyLibPart.DateTimeField._value = patch_date_time_value