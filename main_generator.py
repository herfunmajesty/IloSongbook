import os

import datetime
import shutil
from jinja2 import Environment, FileSystemLoader

from Song import Song
from SongCollection import SongCollection
from song_parser import process_song_file
from html_genetator import generate_index, generate_song_html, generate_song_list_html


sep1 = "\n===================\n"
sep2 = "\n-------------------\n"
sep3 = "======"


def read_songs_from_folder(local_folder_path):  #
    songs = []

    for filename in os.listdir(local_folder_path):
        # print(f'==========\n{filename}\n============')
        if filename.endswith('.txt'):
            if not filename.startswith("_"):  # zostawiam tę część dla ignorowania templatki - zrobić jej update
                print(f'Czytam {filename}')
                file_path = os.path.join(local_folder_path, filename)
                file_content = read_song_file (file_path)
                
                
                loc_song = process_song_file(file_content, filename)
                songs.append(loc_song)
        else:
            log_sequence(filename, "Nazwa zaczyna się od _")
    # zapis do innego loga zrobić - że taka i taka piosenka się zaczytała
    print(f'{sep3} Ive got all songs {sep3}')
    return songs


def read_song_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as loc_file:
        return loc_file.read()

def print_songs_details(loc_songs_list):
    print(f'{sep1}')  # Separator dla czytelności
    for x_song in loc_songs_list:
        print(f"Title: {x_song.Title}")
        print(f'nazwa html:{x_song.html_name}')
        print(f"Artist: {x_song.Artist}")
        print(f"Level: {x_song.Level}")
        print(f"rodzaj lewela: {x_song.l_tr}")
        print(f"Spotify Link: {x_song.s_link}")
        print(f"YouTube Link: {x_song.y_link}")
        print(f"Chords list: {x_song.ch_list}")
        # print(f"Lyrics and Chords: {x_song.lyrics}")
        print(f"Duration: {x_song.Duration}")
        print(f"Czy jest sticky: {x_song.Sticky}")
        print(f"{sep2}")  # Separator dla czytelności


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

# ====================== Program Własciwy ===========================



def build_songbook():
    # raise Exception ('testowy błąd gui')
    result = {
        "success": False,
        "active": 0,
        "archive": 0,
        "test": 0,
        "warnings": [],
        "errors": []
    }
    

    print(f"{sep1}Tworzenie bazy piosenek aktywnych{sep1}")
    print("Current working directory:", os.getcwd())

    # kopiowanie obrazów i ikon do katalogu wyjsciowego
    img_folders = ['images', 'chords']
    src_directory = os.path.join(os.getcwd(), 'in')
    dest_directory = os.path.join(os.getcwd(), 'out')
    copy_folders(src_directory, dest_directory, img_folders)
    # kopiowanie plików nie renderowanych
    n_r_files = ['how.html']
    n_src_directory = os.path.join(os.getcwd(), 'in/template')
    n_dest_directory = os.path.join(os.getcwd(), 'out')
    copy_files(n_src_directory, n_dest_directory, n_r_files)

    # Najpierw tworzę bazę piosenek aktywnych:
    folder_path_active = os.path.join(os.getcwd(), 'in/songs/active')
    print(f'{sep2}Funkcja zaczytująca z plików{sep2}')
    songs_list = read_songs_from_folder(folder_path_active)

    # print(f'{sep2} drukuję szczegóły po zaczytaniu!{sep2}')
    print_songs_details(songs_list)

    collection = SongCollection()
    # Dodaj wszystkie piosenki do kolekcji
    for song in songs_list:
        # print(f'Dodaję do collection piosenkę: {Song.Title}')
        collection.add_song(song)

    print(f"{sep3}Ile piosenek jest na liście?{sep3}")  # Separator dla czytelności
    songTotal = collection.count_songs()
    result["active"]=songTotal
    print(collection.count_songs())
    print(f"{sep2}")  # Separator dla czytelności

    # Posortuj piosenki i przypisz im numery
    collection.sort_songs()
    collection.assign_numbers('')
    for song in collection:
        print(f"{song.Number} --- {song.Title}  --  by   {song.Artist}")

    main_directory = "out"
    generate_index(main_directory)
    generate_song_html(collection, main_directory, 'song.html')
    list_name = "songs"  # zmienic ten fragment na main_list i zaimplementować w html
    generate_song_list_html(collection, main_directory, 'songs.html', list_name)

    #    USUNIETE

    # to do:
    # szablon listy
    # adres wstecza w szablonie poisenki

    print(f"{sep1}Tworzenie bazy piosenek usuniętych{sep1}")
    # Najpierw tworzę bazę piosenek usuniętych:
    folder_path_archive: str = os.path.join(os.getcwd(), 'in/songs/archive')
    print(folder_path_archive)
    print(f'{sep2}Funkcja zaczytująca z plików{sep2}')

    songs_list_archive = read_songs_from_folder(folder_path_archive)

    arch_collection = SongCollection()
    # Dodaj wszystkie piosenki do kolekcji
    for song in songs_list_archive:
        # print(f'Dodaję do collection piosenkę: {Song.Title}')
        arch_collection.add_song(song)

    print(f"{sep3}Ile piosenek jest na liście archiwalnej?{sep3}")  # Separator dla czytelności
    a_songTotal = arch_collection.count_songs()
    result["archive"]=a_songTotal
    print(a_songTotal)
    print(f"{sep2}")  # Separator dla czytelności

    # Posortuj piosenki i przypisz im numery
    arch_collection.sort_songs()
    arch_collection.assign_numbers('A')
    for song in arch_collection:
        print(f"{song.Number} --- {song.Title}  --  by   {song.Artist}")

    directory = "out/archive"
    generate_song_html(arch_collection, directory, 'song_hidden.html')
    a_list_name = "archive"  # zmienic ten fragment na archive_list i zaimplementować w html
    generate_song_list_html(arch_collection, directory, 'songs_hidden.html',  a_list_name)


    #    NOWE - TESTOWE
    # to do:
    # szablon listy
    # adres wstecza w szablonie poisenki

    print(f"{sep1}Tworzenie bazy piosenek  do testów{sep1}")
    # Najpierw tworzę bazę piosenek usuniętych:
    folder_path_test: str = os.path.join(os.getcwd(), 'in/songs/new')
    print(folder_path_test)
    print(f'{sep2}Funkcja zaczytująca z plików{sep2}')

    songs_list_test = read_songs_from_folder(folder_path_test)

    test_collection = SongCollection()
    # Dodaj wszystkie piosenki do kolekcji
    for song in songs_list_test:
        # print(f'Dodaję do collection piosenkę: {Song.Title}')
        test_collection.add_song(song)

    print(f"{sep3}Ile piosenek jest na liście testowej?{sep3}")  # Separator dla czytelności
    n_songTotal = test_collection.count_songs()
    result["test"]=n_songTotal
    print(n_songTotal)
    print(f"{sep2}")  # Separator dla czytelności

    # Posortuj piosenki i przypisz im numery
    test_collection.sort_songs()
    test_collection.assign_numbers('T')
    for song in test_collection:
        print(f"{song.Number} --- {song.Title}  --  by   {song.Artist}")

    directory2 = "out/new"
    generate_song_html(test_collection, directory2, 'song_hidden.html')
    t_list_name = "test"  # zmienic ten fragment na test_list i zaimplementować w html
    generate_song_list_html(test_collection, directory2, 'songs_hidden.html',  t_list_name)
    result["success"]="True"
    return result

if __name__=="__main__":
    result=build_songbook()
    print('\nWYNIK BUILD:')
    print(result)

