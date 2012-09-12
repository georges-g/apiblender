import os

# File system paths
local_path = os.path.dirname(__file__)
general_json_path = os.path.join(local_path, 'config', 'general.json')
apis_folder_path = os.path.join(local_path, 'config', 'apis')
auth_folder_path = os.path.join(apis_folder_path, 'auth')
