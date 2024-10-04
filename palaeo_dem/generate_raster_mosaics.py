'''
Created on Sep 24, 2024

@author: kjsmi
'''
import os
from palaeo_dem import tiles_to_raster

# Point the script towards the 'rasters' folder.
base_dir = r'E:\GIS\Maritime_Encounters\Rasters'

pr_list = []

# Format is {basename for output: path to folder,...}
#mosaic_folder_dict = {'SRTM': r'E:\GIS\Maritime_Encounters\Rasters\SRTM'}
#mosaic_folder_dict = {'EMODNET': r'E:\GIS\Maritime_Encounters\Rasters\EMODNET\EMODNET_Tiles'}
mosaic_folder_dict = {'SRTM_EMODNET_comp': r'E:\GIS\Maritime_Encounters\Rasters\EMODNET_SRTM_Compromise'}

country_codes = ['BE','DE','ES','FR','IE','LU','NL','UK']
#country_codes = ['ES', 'UK']

# Add folders as appropriate. Filename is based on shallowest directory.
for out_basename in mosaic_folder_dict.keys():
    
    mosaic_folder = mosaic_folder_dict[out_basename]
    
    # Add country code as appropriate.
    for country_code in country_codes:
        
        # Derive polygon path.
        poly_path = os.path.join(base_dir, country_code, "Polygon_Mask", "geoBoundaries_CGAZ_ADM0_{}.shp".format(country_code))
        
        # Check that polygon path exists.
        if os.path.exists(poly_path):
            
            out_filename = "{}_mosaic_{}.tif".format(out_basename, country_code)
            out_filepath = os.path.join(base_dir, country_code, out_filename)
    
            tiles_to_raster.tiles_to_raster(poly_path, mosaic_folder, out_filepath)
            
        else:
            
            print("Could not find polygon file '{}'. Check datasets and try again.".format(poly_path))