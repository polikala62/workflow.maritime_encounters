'''
Created on Aug 13, 2024

@author: kjsmi
'''
import arcpy, os, json, datetime
from arcpy.sa import FocalStatistics, Raster, NbrCircle, NbrAnnulus
from palaeo_dem import adjacent_tiles_dict, check_crs, replace_raster, track_completion

def generalise_raster_tiles(in_dir, out_dir, check_extension, in_remove_fc, pixel_type, line_buffer_dist, generalise_dist, out_resolution,
                            adjacency_json="", generalise_type="CIRCLE", append_to_output_filename=""):
    
    print("Started script 'generalise_raster_tiles'.")
    
    arcpy.env.overwriteOutput = True
    
    # Calculate buffer distance based on crs resolution and window size.
    pr_crs = check_crs.check_crs(in_dir, check_extension)
    #pr_crs_res = pr_crs.XYResolution
    #pr_buffer_distance = pr_crs_res * (window_max_size + 1) # Play it safe.
    pr_buffer_distance = generalise_dist
    
    # Build dictionary for adjacent tiles.
    print("Building / importing adjacency dictionary...")
    if adjacency_json == "":
        adjacent_tile_dict = adjacent_tiles_dict.adjacent_tiles_dict(in_dir, check_extension, in_crs=pr_crs, buffer_distance=pr_buffer_distance)
    elif os.path.exists(adjacency_json):
        with open(adjacency_json) as json_file:
            adjacent_tile_dict = json.load(json_file)
    else:
        raise Exception("Adjacency json {} does not exist.".format(adjacency_json))
    
    # Create list to hold datetime objects for progress notification.
    pr_timedelta_list = []
    
    # Loop through files in input to find the number of files to process.
    pr_total = 0
    for root, dirs, files in os.walk(in_dir, topdown=False):
        
        for name in files:
            
            if str(name).endswith(check_extension):
                
                pr_total += 1
    
    # Loop through files in input.
    print("Processing tiles...")
    for root, dirs, files in os.walk(in_dir, topdown=False): #@UnusedVariables
        
        for name in files:
            
            if str(name).endswith(check_extension):
                
                start_time = datetime.datetime.now()
                
                # Get path to raster.
                iter_path = os.path.join(root, name)
                iter_basename, iter_extension = name.split(".")
                
                # Get extent.
                iter_extent = Raster(iter_path).extent
                
                # Get extent for buffered raster. CLUNKY - REPLACE WITH MORE EFFICIENT FUNCTION IF NECESSARY.
                arcpy.env.extent = adjacent_tiles_dict.raster_extent_buffer(iter_path, pr_buffer_distance, pr_crs).extent
                
                # Get list of rasters to mosaic.
                if iter_path in adjacent_tile_dict.keys():
                    mosaic_list = adjacent_tile_dict[iter_path]
                    
                else:
                    mosaic_list = [iter_path]
                    
                # Create raster to generalise.
                pr_mosaic_path = r'in_memory\pr_mosaic'
                #print("Mosaicing...")
                arcpy.management.MosaicToNewRaster(mosaic_list, r'in_memory', r'pr_mosaic', 
                                                   coordinate_system_for_the_raster=pr_crs, 
                                                   pixel_type=pixel_type, number_of_bands=1, mosaic_method="FIRST")
                
                # Load raster object.
                mosaic_raster = Raster(pr_mosaic_path)
                
                # Delete raster file to free up memory.
                #arcpy.management.Delete(pr_mosaic_path)
                # Set extent to the extent of the iterated raster (again, just in case).
                arcpy.env.extent = iter_extent
                #print("Resampling...")
                # Copy raster with the new extent.
                #mod_raster.save(out_path)
                pr_resample_path = r'in_memory\pr_resample'
                #arcpy.management.CopyRaster(pr_mod_raster_path, out_path)
                arcpy.management.Resample(mosaic_raster, pr_resample_path, out_resolution, "CUBIC")
                resample_raster = Raster(pr_resample_path)
                
                # Create generalised raster.
                if generalise_type=="CIRCLE":
                    mod_neighbourhood = NbrCircle(generalise_dist, "MAP")
                elif generalise_type=="ANNULUS":
                    mod_neighbourhood = NbrAnnulus(line_buffer_dist, generalise_dist, "MAP")
                #print("Focalstatsing...")
                mod_raster = FocalStatistics(resample_raster, neighborhood=mod_neighbourhood, 
                                             statistics_type="MEAN", ignore_nodata="DATA")
                
                # Combine input and generalised rasters.
                
                # Set extent to the extent of the iterated raster.
                arcpy.env.extent = iter_extent
                
                # Create path for export.
                out_path = os.path.join(out_dir, "{}{}.{}".format(iter_basename, append_to_output_filename, iter_extension))
                #print("Substituting...")
                sub_raster = replace_raster.replace_raster(resample_raster, mod_raster, in_remove_fc, pr_crs, iter_extent, buffer_distance=line_buffer_dist)
                
                # Set extent to the extent of the iterated raster (again, just in case).
                arcpy.env.extent = iter_extent
                
                # Copy raster with the new extent.
                sub_raster.save(out_path)
                #arcpy.management.CopyRaster(pr_mod_raster_path, out_path)
                '''
                print("Resampling...")
                arcpy.management.Resample(sub_raster, out_path, out_resolution, "CUBIC")
                '''
                # Delete raster objects.
                del mosaic_raster, mod_raster, sub_raster, resample_raster
                
                pr_time = datetime.datetime.now()-start_time
                pr_timedelta_list.append(pr_time)
                track_completion.prcnt_complete(pr_timedelta_list, pr_total, pr_time, 
                                                prcnt_inc=1, leading_spaces=2, leading_text="Tile processing", timedelta_span=0, method="SIMPLE")
                #print("Processed {}.".format(iter_path))
    
    print("Script finished!")
                
generalise_raster_tiles(r'D:\GIS\ME_Rasters\NL\AHN_DEM_50CM', r'D:\GIS\ME_Rasters\NL\AHN_DEM_corrected_v1',
                        '.tif', r'C:\GIS\Maritime_Encounters\PalaeoDEM\ME_PalaeoDEM\Features\NL_roads_canals.shp', 
                        pixel_type="16_BIT_SIGNED", line_buffer_dist=50, generalise_dist=500, out_resolution=10,
                        adjacency_json=r"D:\GIS\ME_Rasters\NL\json\AHN_DEM_50CM_adjacency.json", 
                        generalise_type="ANNULUS", append_to_output_filename="_v1")