import json
import os
current_path = os.getcwd()
file_path = os.path.join(current_path, 'vendor_config.json')

with open(file_path, 'r') as file:
    vendor_config = json.load(file)
    vendor_config = vendor_config["vendor_config"]