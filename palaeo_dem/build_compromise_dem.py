'''
Created on Sep 25, 2024

@author: kjsmi
'''

import arcpy, datetime, os
from arcpy.sa import *

def mosaic_from_folder(in_folder, out_raster_path, in_extent="", check_extensions=['.TIF', '.tif']):
    
    arcpy.env.overwriteOutput = True
    arcpy.env.resamplingMethod = "BILINEAR"
        
    pr_tile_list = []
    
    for root, dirs, files in os.walk(in_folder, topdown=False): #@UnusedVariables
        
        for name in files:
            
            if True in [str(name).endswith(check_extension) for check_extension in check_extensions]:
                
                # Add tile path to list.
                pr_tile_list.append(os.path.join(root, name))
                
    if in_extent != "":
        arcpy.env.extent = in_extent
        
        # Add constant raster to the end of the list, set value to zero.
        pr_tile_list.append(CreateConstantRaster(0, data_type="INTEGER", extent=in_extent))
                
    # Mosaic tiles to new raster.
    arcpy.management.MosaicToNewRaster(pr_tile_list, os.path.dirname(out_raster_path), os.path.basename(out_raster_path), pixel_type="16_BIT_SIGNED", number_of_bands=1, mosaic_method="FIRST")


def build_compromise_dem(srtm_tile_folder, emodnet_tile_folder, out_folder):
    
    arcpy.env.overwriteOutput = True
    arcpy.env.resamplingMethod = "BILINEAR"
    
    srtm_mosaic_path = os.path.join(out_folder, "srtm_mosaic.tif")
    emodnet_mosaic_path = os.path.join(out_folder, "emodnet_mosaic.tif")
    
    
    print("{}: Mosaicing tiles...".format(str(datetime.datetime.now())))
    mosaic_from_folder(emodnet_tile_folder, emodnet_mosaic_path)
    
    # Set extent to the extent of the EMODNET dataset, which is bigger.
    emodnet_extent = Raster(emodnet_mosaic_path).extent
    arcpy.env.extent = emodnet_extent
    
    mosaic_from_folder(srtm_tile_folder, srtm_mosaic_path, in_extent=emodnet_extent)
    
    # Set snap raster to the SRTM dataset, which is more detailed.
    arcpy.env.snapRaster = srtm_mosaic_path
    
    srtm_nonulls_path = srtm_mosaic_path
    emodnet_nonulls_path = emodnet_mosaic_path
    
    '''
    # To override extents I had to add a constant raster to the mosaic function, which accomplishes the same thing as Con(IsNull...). Code may still be useful tho!
    print("{}: Setting mosaic null values to zero...".format(str(datetime.datetime.now())))
    srtm_nonulls_path = os.path.join(out_folder, "srtm_nonulls.tif")
    emodnet_nonulls_path = os.path.join(out_folder, "emodnet_nonulls.tif")
    
    emodnet_nonulls_raster = RasterCalculator([emodnet_mosaic_path], ["x"], 'Con(IsNull(x),0, x)')
    emodnet_nonulls_raster.save(emodnet_nonulls_path)
    
    srtm_nonulls_raster = RasterCalculator([srtm_mosaic_path], ["x"], 'Con(IsNull(x),0, x)')
    srtm_nonulls_raster.save(srtm_nonulls_path)
    '''
    
    print("{}: Generating raster mask...".format(str(datetime.datetime.now())))
    mask_path = os.path.join(out_folder, "comp_mask.tif")
    mask_raster = RasterCalculator([srtm_nonulls_path, emodnet_nonulls_path], ["srtm", "emodnet"], '(emodnet < srtm) & (srtm <= 0)')
    mask_raster.save(mask_path)
    
    print("{}: Generating output...".format(str(datetime.datetime.now())))
    out_path = os.path.join(out_folder, "SRTM_EMODNET_comp.tif")
    
    out_raster = Con(mask_raster, emodnet_nonulls_path, srtm_nonulls_path, "Value = 1")
    out_raster.save(out_path)
    
    print("{}: Script finished!".format(str(datetime.datetime.now())))
    
build_compromise_dem(r'E:\GIS\Maritime_Encounters\Rasters\SRTM', r'E:\GIS\Maritime_Encounters\Rasters\EMODNET\EMODNET_Tiles', r'E:\GIS\Maritime_Encounters\SRTM_EMODNET_Compromise')