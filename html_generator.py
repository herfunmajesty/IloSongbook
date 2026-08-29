import datetime
from jinja2 import Environment, FileSystemLoader

sep2 = "\n-------------------\n"


def generate_index(out_dir):
    # print(f"{sep2}Rozpoczynam generowanie index HTML dla bazy songbooka.{sep2}")
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
            youtube=song.y_link,
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

# sprawdzenie gdzie jestem
env = Environment(loader=FileSystemLoader('in/template'))
