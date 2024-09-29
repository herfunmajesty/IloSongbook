import os
import re
import datetime
import shutil
from jinja2 import Environment, FileSystemLoader


sep1 = "\n===================\n"
sep2 = "\n-------------------\n"
sep3 = "======"
# Dictionary with typical phrases to substitute/format for html files
replacements = {
    "<grey>": "<span class='text-muted'>",
    "</grey>": "</span>",
    "[stop]": "<strong>[stop]</strong>",
    "[muted]": "<strong>[muted]</strong>",
    "[riff]": "<span class='text-muted'><strong>(riff)</strong></span>",
    "[back]": "<b><i>",
    "[/back]": "</b></i>",
    """[""": "<span class=\"chord\">[",
    """]""": "]</span>",
    "\n": '<br>',
    # add more if needed here
}

replacements2 = {  # na potrzeby sprawdzania poprawniści tytułu, póki co bez 🔥
    '🎂': '',
    '🎅': '',
    '⭐': ''
    # gdyby mi coś strzeliło i dodałabym więcej ikon to tutaj, ale nie chcę
}


class Song:
    def __init__(self, title, artist, level, s_link, y_link, lyrics, ch_list, duration, sticky):
        self.Title = title
        self.Artist = artist
        self.Level = level
        self.s_link = s_link
        self.y_link = y_link
        self.lyrics = lyrics
        self.ch_list = ch_list
        self.Duration = duration  # na potrzeby autoscrolla
        self.Sticky = sticky   # na potrzeby floatującego okna
        self.l_tr = self.convert_level(level)  # na potrzeby zmyślnego wyświetlania leveli
        self.new = '🔥' in title  # create an attribute 'new' if  🔥 is in the title
        self.html_name = self.convert_name(title)  # bo link umi być legitny
        self.Number = None

    @staticmethod
    def convert_name(title):  # converting title of the song for proper link creation
        html_title = title.replace(' ', '-')
        return html_title

    @staticmethod
    def convert_level(level):  # translating type of level to another variable just for clear visualisation
        if level == "Easy":
            l_tr = "success"
        elif level == "Medium":
            l_tr = "warning"
        elif level == "Hard":
            l_tr = "danger"
        else:
            l_tr = None
        return l_tr


def log_sequence(song_name, message):
    current_time = datetime.datetime.now()  # requires datetime library
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{formatted_time} - Song: {song_name}, Message: {message}"

    # Save  to external txt log
    with open("songbook_log.txt", "a", encoding='utf-8') as log_file:
        log_file.write(log_entry + "\n")


def parse_song_metadata(text):
    metadata_pattern = r"\{(.*?):(.*?)\}"  # scans for {} brackets
    # and inside for the key before : and value after
    metadata_matches = re.findall(metadata_pattern, text)
    metadata_dict = {key.strip(): value.strip() for key, value in metadata_matches}
    return metadata_dict


def normalize_chord(chord):
    # for creating a list of used chords, and then importing schemes
    return chord.replace("\\", "").replace("/", "").replace("#", "sharp")


def extract_chords(text, filename):
    import re

    chords_pattern = r"\[(.*?)\]"
    chords_matches = re.findall(chords_pattern, text)

    # create a list to maintain order and avoid duplicates
    chords_list = []
    seen = set()

    # add chords excluding: (riff, stop, solo itp.)
    seq_count = 0
    for match in chords_matches:
        if not any(keyword in match.lower() for keyword in ['riff', 'stop', 'solo', 'back', 'pause', 'muted', 'NC']):
            normalized_match = normalize_chord(match)
            # if there is sequence of chords with "/", inside, divides, slash was replaced beforehand

            if " " in normalized_match:
                seq_count += 1
                # log_sequence(filename, f'Uwaga!!! mamy zroślaka {normalized_match}')
                sub_chords = normalized_match.split(" ")
                for sub_chord in sub_chords:
                    if sub_chord not in seen:
                        seen.add(sub_chord)
                        chords_list.append(sub_chord)
            else:
                if normalized_match not in seen:
                    seen.add(normalized_match)
                    chords_list.append(normalized_match)

    if seq_count != 0:
        log_sequence(
            filename,
            f'Uwaga! Jest tu {seq_count} zroślaków różnej formy - sprawdź czy akordy'
        )

    return chords_list


def remove_extra_empty_lines(text, max_empty_lines=1):
    # print('Narzędzie do usuwania nadmiarowych linii')
    pattern = r'<br\s*/?>|\n'
    lines = re.split(pattern, text)
    #  print(lines)
    new_lines = []
    empty_line_count = 0

    for line in lines:
        # print (line)
        if line.strip() == '':
            empty_line_count += 1
            # print ('zwiększam licznik pustych nowych linii')
        else:
            empty_line_count = 0
        # print(empty_line_count)
        if empty_line_count <= max_empty_lines:
            new_lines.append(line)
        else: print('Panie, tu jest za dużo pustych linii, co za marnotrastwo, usuwam to w cholere')
    print(new_lines)

    return '<br>'.join(new_lines)


def custom_istitle(string):
    # Usuń znaki specjalne i cyfry
    cleaned_string = re.sub(r"[()'\d]", "", string)

    # Sprawdź, czy oczyszczony string jest sformatowany jako tytuł
    if cleaned_string.istitle():
        return True
    else:
        return False


def check_title(song_name, string):
    # print(string)
    if custom_istitle(string):
        # print(string.strip('.txt').istitle())
        if string.startswith("🔥"):
            if song_name.replace(".txt", "") == string.lstrip("🔥"):
                log_sequence(song_name, "Nowa pisenka, tytuł zgodny")
            else:
                log_sequence(song_name, f'Nowa! Uwaga! Tytuł i nazwa pliku się różnią: {song_name} i {string}')
        else:
            if string.startswith('🎂') or string.startswith('🎅') or string.startswith('⭐'):
                for old, new in replacements2.items():
                    if string.startswith(old):
                        string = string.replace(old, new)
                if song_name.replace(".txt", "") == string:
                    print("Tytuł i nazwa pliku zgodne")
                else:
                    log_sequence(song_name, f'Uwaga! Tytuł ok, ale: nazwa pliku nie: {song_name} i tytuł wew: {string}')
    else:
        # print("źle sformatowany tytul")
        log_sequence(song_name, f"Tytuł jest źle sformatowany wewnątrz pliku!: {string}")


def read_songs_from_folder(local_folder_path):  #
    songs = []
    for filename in os.listdir(local_folder_path):
        # print(f'==========\n{filename}\n============')
        if filename.endswith('.txt'):
            if not filename.startswith("_"):  # zostawiam tę część dla ignorowania templatki - zrobić jej update
                print(f'Czytam {filename}')
                with (open(os.path.join(local_folder_path, filename), 'r', encoding='utf-8') as loc_file):
                    file_content = loc_file.read()
                    metadata = parse_song_metadata(file_content)
                    title = metadata.get('t')
                    print(title)
                    check_title(filename, title)
                    new = True if '🔥' in metadata.get('t') else False
                    # print(new)
                    artist = metadata.get('artist')
                    level = metadata.get('level')
                    s_link = metadata.get('spotify')
                    y_link = metadata.get('youtube')
                    sticky = True
                    # print (sticky)
                    # Ustawienie wartości domyślnej dla czasu trwania na 4, jeśli nie jest podane
                    duration = float(metadata.get('d', 4))
                    # Remove the metadata from the content to get lyrics and chords
                    lyrics_chords_content = re.sub(r"{.*?}", "", file_content)
                    lyrics = lyrics_chords_content
                    # remove_extra_empty_lines(lyrics)
                    # Sprawdzanie i zamiana fraz w zawartości pliku
                    for old, new in replacements.items():
                        if old in lyrics_chords_content:
                            lyrics = lyrics.replace(old, new)
                            # lyrics = lyrics.replace("""[""", "<span class=\"chord\">[")
                            # lyrics = lyrics.replace("""]""", "]</span>")
                    lyrics=remove_extra_empty_lines(lyrics)
                    ch_list = extract_chords(lyrics_chords_content, filename)
                    print(ch_list)
                    loc_song = Song(title, artist, level, s_link, y_link, lyrics, ch_list, duration, sticky)
                    # po nadaniu obiektowu klasy html_namei l_tr nie tworzą się z automatu!
                    html_name = loc_song.convert_name(loc_song.Title)
                    l_tr = loc_song.convert_level(level)
                    print(l_tr)
                    if l_tr is None:
                        print(f'Uwaga! w piosence {filename} coś jest nie tak z levelem')
                        log_sequence(filename, f'Uwaga! w tej piosence coś jest nie tak z levelem, jest: {level}')
                    loc_song = Song(title, artist, level, s_link, y_link, lyrics, ch_list, duration, sticky)
                    print(f'Sprawdzenie poprawności 2: {title}, {html_name}, {level}, {l_tr}')
                    songs.append(loc_song)
        else:
            log_sequence(filename, "Nazwa zaczyna się od _")
    # zapis do innego loga zrobić - że taka i taka piosenka się zaczytała
    print(f'{sep3} I got all songs {sep3}')
    return songs


def generate_index(out_dir):
    print(f"{sep2}Rozpoczynam generowanie index HTML dla bazy songbooka.{sep2}")
    template = env.get_template('index.html')  # Wczytanie szablonu HTML z pliku
    current_time = datetime.datetime.now()  # requires datetime library
    formatted_time = current_time.strftime("%Y-%m-%d")
    html_content = template.render(
        date=formatted_time
    )
    file_name = f"{out_dir}/index.html"
    with open(file_name, 'w', encoding='utf-8') as file:
        print(f'Zapisano html dla indexu {file_name}')
        file.write(html_content)


def generate_song_html(local_song_list, out_dir, template_file):
    # Utworzenie strony pojedynczej piosenki
    print(f"{sep2}Rozpoczynam generowanie plików HTML dla bazy songbooka.{sep2}")
    template = env.get_template(template_file)  # Wczytanie szablonu HTML z pliku

    for song in local_song_list:
        html_content = template.render(
            title=song.Title,
            artist=song.Artist,
            number=song.Number,
            level=song.Level,
            duration=song.Duration,
            lyrics=song.lyrics,
            spotify=song.s_link,
            sticky=song.Sticky,
            chords=song.ch_list,
            ltrans=song.l_tr

        )
        # print(song.Title)
        file_name = f"{out_dir}/{song.html_name}.html"

        with open(file_name, 'w', encoding='utf-8') as file:
            # print(f'Zapisano html do piosenki {file_name}, {song.l_tr}')
            file.write(html_content)


def generate_song_list_html(loc_song_list, out_dir, loc_template, name):
    # Utworzenie strony listy wsystkich piosenek
    template2 = env.get_template(loc_template)  # Wczytanie szablonu listy HTML z pliku

    html_content2 = template2.render(songs=loc_song_list)
    file_name2 = f"{out_dir}/{name}.html"

    with open(file_name2, 'w', encoding='utf-8') as file:
        # print(f'{sep2}Zapisano html do listy piosenek pod nazwa {file_name2}{sep2}')
        file.write(html_content2)


class SongCollection:
    def __init__(self):
        self.songs = []

    def add_song(self, element):
        self.songs.append(element)

    def sort_songs(self):  # Sortowanie piosenek ignorując emotikonę 🔥 🎂 🎅  w tytule
        self.songs.sort(
            key=lambda element: element.Title.replace('🔥', '').replace('🎂', '').replace('🎅', '').replace('⭐', "")
        )

    def assign_numbers(self, prefix):
        for index, element in enumerate(self.songs, start=1):
            element.Number = f'{prefix}{index}'

    def get_songs_by_difficulty(self, *levels):
        # Zwraca listę piosenek o określonych poziomach trudności
        return [element for element in self.songs if element.Level in levels]

    def __iter__(self):
        # Zwraca iterator do listy piosenek
        self._index = 0  # Ustawienie początkowego indeksu dla iteracji
        return self

    def __next__(self):
        # Zwraca kolejny element z listy piosenek
        if self._index < len(self.songs):
            result = self.songs[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration

    def get_new_songs(self):
        return [element for element in self.songs if element.new]

    def count_songs(self):
        return len(self.songs)  # Zwraca liczbę piosenek w liście


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

# sprawdzenie gdzie jestem
env = Environment(loader=FileSystemLoader('in\\template'))
print(f"{sep1}Tworzenie bazy piosenek aktywnych{sep1}")
print("Current working directory:", os.getcwd())

# kopiowanie obrazów i ikon do katalogu wyjsciowego
img_folders = ['images', 'chords']
src_directory = os.path.join(os.getcwd(), 'in')
dest_directory = os.path.join(os.getcwd(), 'out')
copy_folders(src_directory, dest_directory, img_folders)
# kopiowanie plików nie renderowanych
n_r_files = ['how.html']
n_src_directory = os.path.join(os.getcwd(), 'in\\template')
n_dest_directory = os.path.join(os.getcwd(), 'out')
copy_files(n_src_directory, n_dest_directory, n_r_files)

# Najpierw tworzę bazę piosenek aktywnych:
folder_path_active = os.path.join(os.getcwd(), 'in\\songs\\active')
print(f'{sep2}Funkcja zaczytująca z plików{sep2}')
songs_list = read_songs_from_folder(folder_path_active)

# print(f'{sep2} drukuję szczegóły po zaczytaniu!{sep2}')
# print_songs_details(songs_list)

collection = SongCollection()
# Dodaj wszystkie piosenki do kolekcji
for song in songs_list:
    # print(f'Dodaję do collection piosenkę: {Song.Title}')
    collection.add_song(song)

print(f"{sep3}Ile piosenek jest na liście?{sep3}")  # Separator dla czytelności
songTotal = collection.count_songs()
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
folder_path_archive: str = os.path.join(os.getcwd(), 'in\\songs\\archive')
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
print(a_songTotal)
print(f"{sep2}")  # Separator dla czytelności

# Posortuj piosenki i przypisz im numery
arch_collection.sort_songs()
arch_collection.assign_numbers('A')
for song in arch_collection:
    print(f"{song.Number} --- {song.Title}  --  by   {song.Artist}")

directory = "out\\archive"
generate_song_html(arch_collection, directory, 'song_hidden.html')
a_list_name = "archive"  # zmienic ten fragment na archive_list i zaimplementować w html
generate_song_list_html(arch_collection, directory, 'songs_hidden.html',  a_list_name)


#    NOWE - TESTOWE
# to do:
# szablon listy
# adres wstecza w szablonie poisenki

print(f"{sep1}Tworzenie bazy piosenek  do testów{sep1}")
# Najpierw tworzę bazę piosenek usuniętych:
folder_path_test: str = os.path.join(os.getcwd(), 'in\\songs\\new')
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
print(n_songTotal)
print(f"{sep2}")  # Separator dla czytelności

# Posortuj piosenki i przypisz im numery
test_collection.sort_songs()
test_collection.assign_numbers('T')
for song in test_collection:
    print(f"{song.Number} --- {song.Title}  --  by   {song.Artist}")

directory2 = "out\\new"
generate_song_html(test_collection, directory2, 'song_hidden.html')
t_list_name = "test"  # zmienic ten fragment na test_list i zaimplementować w html
generate_song_list_html(test_collection, directory2, 'songs_hidden.html',  t_list_name)
