import shutil
import os

sep3 = "======"

def copy_folders(src_dir, dest_dir, folders_to_copy):

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for folder in folders_to_copy:
        src_path = os.path.join(src_dir, folder)
        dest_path = os.path.join(dest_dir, folder)
        if os.path.exists(src_path):
            shutil.rmtree(dest_path)  # Usuwa istniejący katalog docelowy
            shutil.copytree(src_path, dest_path)
            print(f'Skopiowano {src_path} do {dest_path}')
        else:
            print(f'Folder {src_path} nie istnieje')


def copy_files(src_dir, dest_dir, files_to_copy):

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for file_name in files_to_copy:
        src_path = os.path.join(src_dir, file_name)
        dest_path = os.path.join(dest_dir, file_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f'Skopiowano {src_path} do {dest_path}')
        else:
            print(f'Plik {src_path} nie istnieje')