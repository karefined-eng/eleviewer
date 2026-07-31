from paths import RECENT_FILE_PATH
from save_utils import load_list, save_list, update_list

def load_recent_files(validate=True): return load_list(RECENT_FILE_PATH, validate)
def save_recent_files(files): save_list(RECENT_FILE_PATH, files)
def save_recent_file(path): update_list(RECENT_FILE_PATH, path)
def remove_recent_file(path): update_list(RECENT_FILE_PATH, path, remove=True)
