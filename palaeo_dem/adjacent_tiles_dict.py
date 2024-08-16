'''
Created on Aug 13, 2024

@author: kjsmi
'''

import arcpy, os, datetime, json
from arcpy.sa import Raster
from palaeo_dem import check_crs

def raster_extent_buffer(in_ras, buffer_distance, crs):
    
    pnt_array = arcpy.Array()
    extent = arcpy.Raster(in_ras).extent
    
    arcpy.env.outputCoordinateSystem = crs
    
    out_max_x = extent.XMax+buffer_distance
    out_min_x = extent.XMin-buffer_distance
    out_max_y = extent.YMax+buffer_distance
    out_min_y = extent.YMin-buffer_distance
    
    # Add corners to array.
    pnt_array.add(arcpy.Point(out_min_x, out_max_y)) # NW
    pnt_array.add(arcpy.Point(out_max_x, out_max_y)) # NE
    pnt_array.add(arcpy.Point(out_max_x, out_min_y)) # SE
    pnt_array.add(arcpy.Point(out_min_x, out_min_y)) # SW

    poly = arcpy.Polygon(pnt_array, crs)
    return poly

def raster_corners(in_ras, buffer_distance):
    
    extent = arcpy.Raster(in_ras).extent
    
    out_max_x = extent.XMax+buffer_distance
    out_min_x = extent.XMin-buffer_distance
    out_max_y = extent.YMax+buffer_distance
    out_min_y = extent.YMin-buffer_distance
    
    top_right = arcpy.Point(out_max_x, out_max_y)
    bottom_left = arcpy.Point(out_min_x, out_min_y)
    
    return [top_right, bottom_left]

def coord_overlap(in_coords, check_coords):
    
    in_ne, in_sw = in_coords
    check_ne, check_sw = check_coords
    
    # Check that input ne corner is ne of check sw corner. False means no overlap.
    check_ne_corner = in_ne.X >= check_sw.X and in_ne.Y >= check_sw.Y
    
    # Check that input sw corner is sw of check ne corner. False means no overlap.
    check_sw_corner = in_sw.X <= check_ne.X and in_sw.Y <= check_sw.Y
    
    if check_ne_corner or check_sw_corner:
        
        return True
    
    else:
        
        return False

# Generate dictionary of adjacent tiles by checking the coordinates of each corner.
def adjacent_tiles_dict(in_path, check_extension, buffer_distance=0, in_crs="", out_poly_fc="", include_self=True):
    
    # Create dictionaries for processing and output.
    extent_dict = {}
    out_dict = {}
    
    # Get CRS from folder if not supplied as parameter.
    if in_crs == "":
        pr_crs = check_crs.check_crs(in_path, check_extension)
    else:
        pr_crs = in_crs
    
    # Set CRS as environment setting (might not be necessary?).
    arcpy.env.outputCoordinateSystem = pr_crs
    
    # Create output polygons (if enabled).
    if out_poly_fc != "":
        
        arcpy.env.overwriteOutput = True
        
        arcpy.CreateFeatureclass_management(os.path.dirname(out_poly_fc), os.path.basename(out_poly_fc), "POLYGON", has_z='DISABLED', spatial_reference=pr_crs)
        arcpy.AddField_management(out_poly_fc, "FILENAME", "TEXT")
    
    for root, dirs, files in os.walk(in_path, topdown=False):
        
        for name in files:
            
            if str(name).endswith(check_extension):
                
                iter_path = os.path.join(root, name)
                
                extent_buffer = raster_extent_buffer(iter_path, buffer_distance, pr_crs)
                extent_buffer_coords = raster_corners(iter_path, buffer_distance)
                
                extent_dict[iter_path] = extent_buffer
                
                if out_poly_fc != "":
                    
                    with arcpy.da.InsertCursor(out_poly_fc, ["SHAPE@", "FILENAME"]) as cursor: #@UndefinedVariableFromImport
                        cursor.insertRow([extent_buffer, name])
                
    if len(extent_dict.keys()) > 0:
        
        # Create polygon representing extent for each raster.
        for check_path in extent_dict.keys():
            
            # Create list in dictionary containing iterated path if include_self is enabled, empty list if not.
            if include_self:
                out_dict[check_path] = [check_path]
            else:
                out_dict[check_path] = []
            
            check_extent = extent_dict[check_path]
            
            for check_against_path in extent_dict.keys():
                
                # Don't check raster against self.
                if check_path != check_against_path:
                
                    check_against_extent = extent_dict[check_against_path]
                    
                    # Check if the two extents are disjoint.
                    if check_extent.overlaps(check_against_extent):
                        
                        out_dict[check_path].append(check_against_path)
                        
        return out_dict
    
    else:
        
        raise Exception("No valid files within '{}'. Check path or extension.".format(in_path))

def adjacent_tiles_json(in_path, check_extension, out_json, buffer_distance=0, in_crs="", out_poly_fc="", include_self=True):
    
    out_dict = adjacent_tiles_dict(in_path, check_extension, buffer_distance, in_crs, out_poly_fc, include_self)
    
    with open(out_json, 'w', encoding='utf-8') as f:
        
        json.dump(out_dict, f, ensure_ascii=False, indent=4)

#adjacent_tiles_json(r'D:\GIS\ME_Rasters\NL\AHN_DEM_50CM', '.tif', r'D:\GIS\ME_Rasters\NL\json\AHN_DEM_50CM_adjacency.json', buffer_distance=5)
