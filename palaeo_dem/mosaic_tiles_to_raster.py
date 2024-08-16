'''
Created on Aug 16, 2024

@author: kjsmi
'''
import arcpy, os

def mosaic_tiles(in_dir, check_extension, out_path, pixel_type=, number_of_bands=1, mosaic_method="FIRST"):
    
    mosaic_list = []
    
    for root, dirs, files in os.walk(in_dir, topdown=False): #@UnusedVariables
        
        for name in files:
            
            if str(name).endswith(check_extension):
                
                mosaic_list.append(os.path.join(root, name))
    
    coordinate_system_for_the_raster = ""
    
    arcpy.management.MosaicToNewRaster(mosaic_list, r'in_memory', r'pr_mosaic', 
                                       coordinate_system_for_the_raster, 
                                       pixel_type, number_of_bands, mosaic_method)