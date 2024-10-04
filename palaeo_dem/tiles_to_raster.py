'''
Created on Sep 24, 2024

@author: kjsmi
'''

import arcpy, datetime, os
from arcpy.sa import *

def tiles_to_raster(in_shapefile, in_tile_folder, out_raster_path, check_extensions=['.TIF', '.tif']):
    
    print("Generating mosaic for '{}'...".format(in_shapefile))
    
    # Allow overwrite.
    arcpy.env.overwriteOutput = True
    
    # Get extent from input shapefile.
    print("  Dissolving shapefile...")
    
    # Dissolve to temporary shapefile.
    arcpy.management.Dissolve(in_shapefile, r'in_memory\dissolve_features')
    
    # Get geometry of first (and only) feature in shapefile.
    with arcpy.da.SearchCursor(in_shapefile,['SHAPE@']) as cursor:
        for row in cursor:
            shapefile_geometry = row[0]
    
    # Loop through rasters in folder and subfolders, add rasters to list if raster extent overlaps with shapefile extent.
    
    # Loop through files in input.
    print("  Processing tiles...")
    
    pr_tile_list = []
    
    for root, dirs, files in os.walk(in_tile_folder, topdown=False): #@UnusedVariables
        
        for name in files:
            
            if True in [str(name).endswith(check_extension) for check_extension in check_extensions]:
                
                # Get path to raster.
                iter_path = os.path.join(root, name)
                
                # Get extent.
                iter_extent = Raster(iter_path).extent
                
                # Check extent against polygon.
                if iter_extent.disjoint(shapefile_geometry) == False:
                    
                    pr_tile_list.append(iter_path)
    
    # Check that rasters were identified.
    if len(pr_tile_list) == 0:
        
        print("  No tiles found! Check files or input coordinate systems.")
        
    else:
        
        print("  Mosaicing {} rasters to new dataset...".format(len(pr_tile_list)))
        
        # Run Mosaic to New Raster.
        out_raster_basename = os.path.basename(out_raster_path)
        out_raster_folder = os.path.dirname(out_raster_path)
        arcpy.management.MosaicToNewRaster(pr_tile_list, out_raster_folder, out_raster_basename, pixel_type="16_BIT_SIGNED", number_of_bands=1,)
        
    print("Created mosaic.")
        
        