'''
Created on Aug 5, 2024

@author: kjsmi
'''
import arcpy
from arcpy.sa import *

arcpy.env.overwriteOutput = True

def raster_extent_buffer(in_ras, buffer_distance, crs):
    
    pnt_array = arcpy.Array()
    extent = arcpy.Raster(in_ras).extent
    
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

def replace_raster(in_base_raster, in_smooth_raster, in_lines, in_polygons, in_crs, iter_extent, out_raster_path="", buffer_distance=0):
    
    # Set environment variables.
    arcpy.env.extent = iter_extent
    arcpy.env.snapRaster = in_base_raster
    arcpy.env.outputCoordinateSystem = in_crs
    
    # Clip lines to base raster extent.
    clip_lines_fc = r'in_memory\clip_lines'
    arcpy.Clip_analysis(in_lines, raster_extent_buffer(in_base_raster, buffer_distance, in_crs), clip_lines_fc)
    
    # Buffer lines.
    buffer_lines_fc = r'in_memory\buffer_lines'
    arcpy.analysis.Buffer(clip_lines_fc, buffer_lines_fc, buffer_distance)
    
    # Combine buffer with polygons (if they exist).
    if in_polygons == "":
        merge_poly_fc = buffer_lines_fc
        
    else:
        merge_poly_fc = r'in_memory\buffer_lines\merge_poly'
        arcpy.management.Merge([buffer_lines_fc, in_polygons], merge_poly_fc)
        
    
    # Convert polygon features to raster.
    raster_to_polygon_fc = r'in_memory\raster_to_poly'
    conv_field = [f.name for f in arcpy.ListFields(merge_poly_fc, field_type="OID")][0]
    arcpy.conversion.PolygonToRaster(merge_poly_fc, conv_field, raster_to_polygon_fc, cellsize=in_base_raster)
    
    # Reclassify raster to create polygon mask, where 1 = Null and 0 = everything else.
    isnull_raster = IsNull(raster_to_polygon_fc)
    
    # Run raster calculator.
    out_raster = Con(isnull_raster, in_base_raster, in_smooth_raster, "VALUE > 0")
    
    # Return raster object if no raster path is set.
    if out_raster_path == "":
        return out_raster
    else:
        out_raster.save(out_raster_path)

"""
def replace_raster_with_polygon(in_base_raster, in_replace_raster, in_polygons, in_crs, iter_extent, out_raster_path="", buffer_distance=0):
    
    # Set environment variables.
    arcpy.env.extent = iter_extent
    arcpy.env.snapRaster = in_base_raster
    arcpy.env.outputCoordinateSystem = in_crs
    
    # Clip lines to base raster extent.
    clip_lines_fc = r'in_memory\clip_lines'
    arcpy.Clip_analysis(in_polygons, raster_extent_buffer(in_base_raster, buffer_distance, in_crs), clip_lines_fc)
    
    # Convert polygon features to raster.
    raster_to_polygon_fc = r'in_memory\raster_to_poly'
    conv_field = [f.name for f in arcpy.ListFields(in_polygons, field_type="OID")][0]
    arcpy.conversion.PolygonToRaster(clip_lines_fc, conv_field, raster_to_polygon_fc, cellsize=in_base_raster)
    
    # Reclassify raster to create polygon mask, where 1 = Null and 0 = everything else.
    isnull_raster = IsNull(raster_to_polygon_fc)
    
    # Run raster calculator.
    out_raster = Con(isnull_raster, in_base_raster, in_replace_raster, "VALUE > 0")
    
    # Return raster object if no raster path is set.
    if out_raster_path == "":
        return out_raster
    else:
        out_raster.save(out_raster_path)

'''
replace_raster(r'C:\GIS\Maritime_Encounters\PalaeoDEM\ME_PalaeoDEM\Test\base_01.tif',
               r'C:\GIS\Maritime_Encounters\PalaeoDEM\ME_PalaeoDEM\Test\smooth_01.tif',
               r'C:\GIS\Maritime_Encounters\PalaeoDEM\ME_PalaeoDEM\Test\lines_01.shp',
               r'C:\GIS\Maritime_Encounters\PalaeoDEM\ME_PalaeoDEM\Test\out_test_01.tif')
'''
"""
pass