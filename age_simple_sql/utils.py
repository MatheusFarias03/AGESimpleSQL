'''
AGESimpleSQL utility functions
'''

# I don't really know what I did here. But it shows right I guess.
def format_properties(v_properties:dict) -> str:
    '''
    Convert dictionary items to strings for openCypher syntax
    '''
    prop = '{'
    for k, v in v_properties.items():
        v = v.replace("\"", "'")
        prop += f'{k}: "{v}", ' 
    prop = prop[:-2] # Remove the last comma.
    prop += '}'
    return prop