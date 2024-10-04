'''
Created on Sep 18, 2024

@author: kjsmi
'''
import os
from palaeo_dem import adjacent_tiles_dict



pr_dict = {"FLANDERS":[r'E:\GIS\Maritime_Encounters\Rasters\BE\Flanders\Tiles', '.tif', ""],
           "NIEDERSACHSEN":[r'E:\GIS\Maritime_Encounters\Rasters\DE\Niedersachsen\tiles', '.tif', ""],
           "SPAIN":[r'E:\GIS\Maritime_Encounters\Rasters\ES\DTM_5M', '.tif', ""],
           "FRANCE":[r'E:\GIS\Maritime_Encounters\Rasters\FR\Tiles', '.asc', "_MNT_"],
           "NETHERLANDS":[r'E:\GIS\Maritime_Encounters\Rasters\NL\AHN_1_DTM_5M\Tiles', '.tif', ""]}

process_keys_list = []

for key in pr_dict.keys():

    if key in process_keys_list:
        
        in_path, check_extension, filter_str = pr_dict[key]
        
        out_fc = os.path.join(os.path.dirname(in_path), "tile_grid_{}.shp".format(key.lower()))

        adjacent_tiles_dict(in_path, check_extension, out_poly_fc=out_fc, filter_text=filter_str)