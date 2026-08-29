import re

from reporting import log_sequence

replacements2 = {  # na potrzeby sprawdzania poprawniści tytułu, póki co bez 🔥
    '🎂': '',
    '🎅': '',
    '⭐': ''
    # gdyby mi coś strzeliło i dodałabym więcej ikon to tutaj, ale nie chcę
}

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

def custom_istitle(string):
    # Usuń znaki specjalne i cyfry
    cleaned_string = re.sub(r"[()'\d]", "", string)

    # Sprawdź, czy oczyszczony string jest sformatowany jako tytuł
    if cleaned_string.istitle():
        return True
    else:
        return False