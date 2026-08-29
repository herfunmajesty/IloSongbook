import re
from reporting import log_sequence

def normalize_chord(chord):
    # for creating a list of used chords, and then importing schemes
    return chord.replace("\\", "").replace("/", "").replace("#", "sharp")

def extract_chords(text, filename):

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