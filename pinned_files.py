from paths import PINNED_FILE_PATH
from save_utils import load_list, update_list

def load_pinned_files(validate=True): return load_list(PINNED_FILE_PATH, validate)
def save_pinned_file(path): update_list(PINNED_FILE_PATH, path)
def remove_pinned_file(path): update_list(PINNED_FILE_PATH, path, remove=True)
def is_pinned(path): return path in load_list(PINNED_FILE_PATH, validate=False)
