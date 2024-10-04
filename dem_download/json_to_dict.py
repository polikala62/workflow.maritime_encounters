'''
Created on Aug 19, 2024

@author: kjsmi
'''
import json

def json_to_dict_lower_saxony(json_path):
    
    out_list = []
    
    with open(json_path) as json_file:
        parent_dict = json.load(json_file)
        
        for feature_dict in parent_dict['features']:
            out_list.append(feature_dict['properties']['dom1'])
            
    return out_list