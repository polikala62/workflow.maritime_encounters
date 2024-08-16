'''
Created on Aug 13, 2024

@author: kjsmi
'''
import arcpy, os

def check_crs(in_dir, check_extension):
    
    check_list = []
    
    for root, dirs, files in os.walk(in_dir, topdown=False):
        
        for name in files:
            
            if str(name).endswith(check_extension):
                
                iter_path = os.path.join(root, name)
                
                iter_crs = arcpy.Raster(iter_path).extent.spatialReference
                
                if iter_crs not in check_list:
                    
                    check_list.append(iter_crs)
                    
    if len(check_list) == 1:
        
        return check_list[0]
    
    elif len(check_list) == 0:
        
        raise Exception("No files with valid extension / coordinate system found in {}.".format(in_dir))
    
    else:
        
        raise Exception("Files with multiple coordinate systems found in {}.".format(in_dir))