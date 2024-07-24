import os
import re
import pickle
import hashlib

ABILITY_TEMPLATE = 'X2AbilityTemplate'
VALID_PATHS = ["Localization", "Config"]

class XCOM2Parser:
    def __init__(self):
        self.cache_file = 'xcom2_parser_cache.pkl'

    def parse_ini(self, file_path):
        # Existing INI parsing logic
        pass

    def parse_int(self, file_path):
        ability_templates = []
        current_template = None
        try:
            with open(file_path, 'r', encoding='utf-16') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        if current_template:
                            ability_templates.append(current_template)
                        current_template = self.parse_ability_template(line)
                    elif current_template and '=' in line:
                        key, value = line.split('=', 1)
                        current_template[key.strip()] = value.strip().strip('"')
        except Exception as e:
            print(e)
            return None
        if current_template:
            ability_templates.append(current_template)

        return ability_templates

    def parse_ability_template(self, header):
        match = re.match(r'\[(.*?)\s+(.*?)\]', header)
        if match and match.group(2) == ABILITY_TEMPLATE:
            return {
                'Name': match.group(1),
                'Type': match.group(2),
                'LocFriendlyName': '',
                'LocLongDescription': ''
            }
        return None

    def parse_folder(self, folder_path):
        cache = self.load_cache()
        folder_hash = self.hash_folder(folder_path)

        if folder_hash in cache:
            print("Loading data from cache...")
            return cache[folder_hash]

        print("Parsing folder...")
        parsed_data = {
            'ini_files': {},
            'int_files': {}
        }
        for root, _, files in os.walk(folder_path):
            path_end = os.path.basename(os.path.normpath(root))
            if path_end not in VALID_PATHS:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.ini'):
                    parsed_data['ini_files'][file] = self.parse_ini(file_path)
                elif file.endswith('.int'):
                    parsed_data['int_files'][file] = self.parse_int(file_path)

        cache[folder_hash] = parsed_data
        self.save_cache(cache)
        return parsed_data

    def hash_folder(self, folder_path):
        hasher = hashlib.md5()
        for root, _, files in os.walk(folder_path):
            path_end = os.path.basename(os.path.normpath(root))
            if path_end not in VALID_PATHS:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                hasher.update(file_path.encode())
                hasher.update(str(os.path.getmtime(file_path)).encode())
        return hasher.hexdigest()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        return {}

    def save_cache(self, cache):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(cache, f)