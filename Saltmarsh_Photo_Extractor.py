# Code to extract photos from Epicollect5 project Saltmarsh Saver. 
# Photos are saved in a directory structure based on the site name.
# The photo file names are based on the question number and the entry UUID. Code will only work if the photo question is named "XX_Take_a_photo" 
# and the numbers match the below lookup table. If question numbers change the code will still run but the file names won't contain the identifier.
# LS 2024-07-22

import requests
import os
import sys
from tkinter import Tk
from tkinter import filedialog


# Initialize a Tkinter root window
root = Tk()
root.withdraw()  # Hide the root window

# Open a dialog to choose the directory, default to Desktop if none is selected
selected_directory = filedialog.askdirectory(title='Select Folder to Save Photos')
if not selected_directory:
    print("No directory selected, so long and thanks for all the fish....")
    sys.exit()  # Exit the program if no directory is selected
else:
    photo_directory_base = selected_directory

project_slug = 'saltmarsh-saver'
url = f'https://five.epicollect.net/api/export/entries/{project_slug}'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    saltmarsh_photos_directory = os.path.join(selected_directory, 'Saltmarsh Photos')  # Create Saltmarsh Photos directory
    os.makedirs(saltmarsh_photos_directory, exist_ok=True)  # Ensure the Saltmarsh Photos directory exists
    for entry in data['data']['entries']:
        site_name = entry['2_Site_Name'] if entry['2_Site_Name'] != '' else 'Unknown Site'  # Extract site name, default to 'Unknown Site'
        site_directory = os.path.join(saltmarsh_photos_directory, site_name)  # Create a directory path for the site inside Saltmarsh Photos
        os.makedirs(site_directory, exist_ok=True)  # Ensure the site directory exists
        for key, value in entry.items():
            if "Take_a_photo" in key and value:  # Check if the key contains "Take_a_Photo" and has a value
                 # Split the ec5_uuid by '-' and take the first part
                short_uuid = entry["ec5_uuid"].split('-')[0]
                # Determine the file name based on the key
                if "12" in key:
                    file_name = f'fish_access_{short_uuid}.jpg'
                elif "16" in key:
                    file_name = f'fish_access_other_habitats_{short_uuid}.jpg'
                elif "20" in key:
                    file_name = f'density_crab_and_shells_{short_uuid}.jpg'
                elif "24" in key:
                    file_name = f'salt_couch_cover_{short_uuid}.jpg'
                elif "28" in key:
                    file_name = f'habitat_types_present_{short_uuid}.jpg'
                elif "33" in key:
                    file_name = f'vegetation_type_{short_uuid}.jpg'
                elif "37" in key:
                    file_name = f'sediment_type_{short_uuid}.jpg'
                elif "41" in key:
                    file_name = f'vegetation_cover_{short_uuid}.jpg'
                elif "46" in key:
                    file_name = f'vegetation_density_{short_uuid}.jpg'
                elif "50" in key:
                    file_name = f'algal_mat_cover_{short_uuid}.jpg'
                elif "54" in key:
                    file_name = f'stormwater_proximity_{short_uuid}.jpg'
                elif "58" in key:
                    file_name = f'nutrient_pollution_proximity_{short_uuid}.jpg'
                elif "62" in key:
                    file_name = f'indirect_runoff_connectivity_{short_uuid}.jpg'
                elif "66" in key:
                    file_name = f'tidal_channel_connectivity_{short_uuid}.jpg'
                elif "71" in key:
                    file_name = f'migratory_bird_presence_{short_uuid}.jpg'
                elif "75" in key:
                    file_name = f'threatened_species_presence_{short_uuid}.jpg'
                elif "79" in key:
                    file_name = f'locally_iconic_species_presence_{short_uuid}.jpg'
                elif "83" in key:
                    file_name = f'general_habitat_values_{short_uuid}.jpg'
                elif "88" in key:
                    file_name = f'recreational_accessibilty_{short_uuid}.jpg'
                elif "92" in key:
                    file_name = f'visual_appeal_{short_uuid}.jpg'
                elif "97" in key:
                    file_name = f'adjacent_habitat_landuse_infrastructure_{short_uuid}.jpg'
                elif "101" in key:
                    file_name = f'cultural_value_{short_uuid}.jpg'
                elif "106" in key:
                    file_name = f'tyre_track_damage_{short_uuid}.jpg'
                elif "110" in key:
                    file_name = f'cattle_damage_{short_uuid}.jpg'
                elif "114" in key:
                    file_name = f'feral_animal_damage_{short_uuid}.jpg'
                elif "118" in key:
                    file_name = f'mowing_damage_{short_uuid}.jpg'
                elif "122" in key:
                    file_name = f'fire_damage_{short_uuid}.jpg'
                elif "126" in key:
                    file_name = f'human_trampling_{short_uuid}.jpg'
                elif "131" in key:
                    file_name = f'surface_erosion_{short_uuid}.jpg'
                elif "135" in key:
                    file_name = f'sediment_burial_{short_uuid}.jpg'
                elif "139" in key:
                    file_name = f'shoreline_erosion_{short_uuid}.jpg'
                elif "144" in key:
                    file_name = f'litter_{short_uuid}.jpg'
                elif "149" in key:
                    file_name = f'habitat_replacement_{short_uuid}.jpg'
                elif "154" in key:
                    file_name = f'agricultural_runoff_likelihood_{short_uuid}.jpg'
                elif "158" in key:
                    file_name = f'urban_runoff_likelihood_{short_uuid}.jpg'
                elif "163" in key:
                    file_name = f'herbicide_damage_{short_uuid}.jpg'
                elif "167" in key:
                    file_name = f'chemical_pollution_potential_{short_uuid}.jpg'  
                elif "172" in key:
                    file_name = f'tidal_flow_changes_{short_uuid}.jpg'
                elif "176" in key:
                    file_name = f'freshwater_flow_changes_{short_uuid}.jpg'
                elif "181" in key:
                    file_name = f'buffer_zone_condition_{short_uuid}.jpg'
                elif "185" in key:
                    file_name = f'coastal_squeeze_{short_uuid}.jpg'
                elif "189" in key:
                    file_name = f'terretrial_retreat_{short_uuid}.jpg'
                elif "193" in key:
                    file_name = f'mangrove_encroachment_{short_uuid}.jpg'
                elif "197" in key:
                    file_name = f'weeds_{short_uuid}.jpg'
                elif "201" in key:
                    file_name = f'drought_water_stress_{short_uuid}.jpg'
                else:
                    file_name = f'{key}_{short_uuid}.jpg'  # Default file name
                # Construct the photo path within the site name directory
                photo_url = value
                photo_path = os.path.join(site_directory, file_name)
                photo_response = requests.get(photo_url)
                if photo_response.status_code == 200:
                    with open(photo_path, 'wb') as photo_file:
                        photo_file.write(photo_response.content)
                    print(f'Downloaded photo to {photo_path}')