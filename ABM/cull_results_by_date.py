'''
Created on Sep 2, 2024

@author: kjsmi
'''
import arcpy, datetime

def cull_results_by_date(in_lines, in_diss_lines, in_points, cull_from_year):
    
    cull_from_datetime = datetime.datetime.strptime("{}-01-01-00-00-00".format(cull_from_year), "%Y-%m-%d-%H-%M-%S")
    cull_id_list = []
    
    # Loop through lines to collect IDs.
    with arcpy.da.SearchCursor(in_lines, ["ID_1", "SIM_DATE"]) as searchcursor: #@UndefinedVariable
                    
        for row in searchcursor:
            
            sim_id, sim_date_string = row
            #mod_sim_date_string = "/".join([i.zfill(2) for i in sim_date_string.split("/")])
            
            sim_datetime = datetime.datetime.strptime(sim_date_string, "%d-%b-%y")
            '''
            sim_datetime = datetime.datetime.strptime(sim_date_string, "%m/%d/%Y")
            '''
            
            if sim_datetime >= cull_from_datetime and sim_id not in cull_id_list:
                cull_id_list.append(sim_id)
    
    print("Found {} IDs to cull.".format(len(cull_id_list)))
    
    # Delete rows from shapefiles.
    for iter_path in [in_lines, in_points]:
        with arcpy.da.UpdateCursor(iter_path, "ID_1") as cursor:
            for row in cursor:
                if row[0] in cull_id_list:
                    cursor.deleteRow()
                    
    with arcpy.da.UpdateCursor(in_diss_lines, "FIRST_ID_1") as cursor:
            for row in cursor:
                if row[0] in cull_id_list:
                    cursor.deleteRow()
                    
    print("Script finished.")
            
            
cull_results_by_date(r'C:\GIS\Maritime_Encounters\OrmeSim\Output\THANET_RUN_1_2015\THANET_RUN_1_2015_lines.shp',
                     r'C:\GIS\Maritime_Encounters\OrmeSim\Output\THANET_RUN_1_2015\THANET_RUN_1_2015_diss_lines.shp',
                     r'C:\GIS\Maritime_Encounters\OrmeSim\Output\THANET_RUN_1_2015\THANET_RUN_1_2015_points.shp',
                     2016)