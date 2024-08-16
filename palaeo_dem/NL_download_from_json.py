'''
Created on Aug 13, 2024

@author: kjsmi
'''


import json, requests, os
import urllib3, shutil

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
                    print(f"Download complete. File saved as {local_filename}")
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

def download_files(json_path, out_dir):
    
    pr_count = 0
    pr_limit = 500
    
    with open(json_path) as json_file:
        kaartbladindex = json.load(json_file)
        features_dict_list = kaartbladindex['features']
            
        for feature_dict in features_dict_list:
            
            feature_url = feature_dict['properties']['url']
            feature_filename = feature_dict['properties']['name']
            
            out_path = os.path.join(out_dir, feature_filename)
            
            if os.path.exists(out_path) == False and pr_count < pr_limit:
                download_large_file(feature_url, out_path)
                
                #pr_count += 1
    
download_files(r'D:\GIS\ME_Rasters\NL\json\AHN_50CM_kaartbladindex.json', r'D:\GIS\ME_Rasters\NL\AHN_DEM_50CM')