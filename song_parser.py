import re

def parse_song_metadata(text):
    metadata_pattern = r"\{(.*?):(.*?)\}"  # scans for {} brackets
    # and inside for the key before : and value after
    metadata_matches = re.findall(metadata_pattern, text)
    metadata_dict = {key.strip(): value.strip() for key, value in metadata_matches}
    return metadata_dict