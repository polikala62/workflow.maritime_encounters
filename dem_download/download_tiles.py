'''
Created on Aug 19, 2024

@author: kjsmi
'''

import json, requests, os, datetime
import urllib3, shutil
from dem_download import json_to_dict, track_completion

def download_large_file(url, local_filename):
    try:
        # Create a PoolManager instance for managing HTTP connections with connection pooling
        with urllib3.PoolManager() as http:
            # Make a GET request with stream=True to download the file in chunks
            with http.request('GET', url, preload_content=False, decode_content=False) as response:
                # Check if the request was successful (status code 200)
                if response.status == 200:
                    # Open a local file for writing in binary mode
                    with open(local_filename, 'wb') as file:
                        # Download the file in chunks and save to the local disk
                        for chunk in response.stream(8192):  # Adjust chunk size as needed
                            file.write(chunk)
                    #print(f"Download complete. File saved as {local_filename}")
                else:
                    print(f"Error: Unable to download file. Status Code: {response.status}")
                    try:
                        os.remove(local_filename)
                    except:
                        print("  Count not remove file.")
    except urllib3.exceptions.RequestError as e:
        print(f"Network Error: {e}")
        try:
            os.remove(local_filename)
        except:
            print("  Count not remove file.")
    except Exception as e:
        print(f"Error: {e}")
        try:
            os.remove(local_filename)
        except:
            print("  Count not remove file.")

def download_tiles(json_path, out_dir):
    
    url_list = json_to_dict.json_to_dict_lower_saxony(json_path)
    timedelta_list = []
    
    check_url_list = []
    for url in url_list:
        out_filename = os.path.basename(url)
        out_path = os.path.join(out_dir, out_filename)
        if os.path.exists(out_path) == False:
            check_url_list.append(url)
    
    print("Downloading {} tiles...".format(len(check_url_list)))
    
    for url in check_url_list:
        
        start_time = datetime.datetime.now()
        
        out_filename = os.path.basename(url)
        out_path = os.path.join(out_dir, out_filename)
            
        download_large_file(url, out_path)
        
        pr_time = datetime.datetime.now() - start_time
        timedelta_list.append(pr_time)
        
        track_completion.prcnt_complete(timedelta_list, len(check_url_list), pr_time, 
                                        prcnt_inc=1, leading_spaces=2, leading_text="Tile downloading", timedelta_span=50, method='SIMPLE')
        

json_path = r"C:\Users\kjsmi\Desktop\lgln-opengeodata-dom1.geojson"
out_dir = r"E:\GIS\ME_Rasters\DE\Niedersachsen\Tiles"
download_tiles(json_path, out_dir)