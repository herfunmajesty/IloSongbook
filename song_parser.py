import re

from validation import check_title
from reporting import log_sequence
from Song import Song
from chord_processing import extract_chords

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
    "<d>": "<span style=\"color: purple;\"><small><i>",
    "</d>": "</i></small></span>",
    "<r>": "<small><b>",
    "</r>": "</b></small>",
    "<s>": "<small><i>",
    "</s>": "</i></small>",
    "\n": '<br>',
    # add more if needed here
}

def parse_song_metadata(text):
    metadata_pattern = r"\{(.*?):(.*?)\}"  # scans for {} brackets
    # and inside for the key before : and value after
    metadata_matches = re.findall(metadata_pattern, text)
    metadata_dict = {key.strip(): value.strip() for key, value in metadata_matches}
    return metadata_dict

def process_song_file(file_content, filename):
    metadata = parse_song_metadata(file_content)
    title = metadata.get('t')
    print(title)
    check_title(filename, title)
    artist = metadata.get('artist')
    level = metadata.get('level')
    s_link = metadata.get('spotify')
    y_link = metadata.get('youtube')
    sticky = True
    # print (sticky)
    # Ustawienie wartości domyślnej dla czasu trwania na 4, jeśli nie jest podane
    duration = float(metadata.get('d', 4))
    lyrics, ch_list = parse_song_content(file_content, filename)
    loc_song = Song(title, artist, level, s_link, y_link, lyrics, ch_list, duration, sticky)
    
    if loc_song.l_tr is None:
        print(f'Uwaga! w piosence {filename} coś jest nie tak z levelem')
        log_sequence(filename, f'Uwaga! w tej piosence coś jest nie tak z levelem, jest: {level}')
    return loc_song

def parse_song_content (file_content, filename):
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
    return lyrics, ch_list

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