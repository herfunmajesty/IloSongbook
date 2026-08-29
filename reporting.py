import datetime

def log_sequence(song_name, message):

    current_time = datetime.datetime.now()  # requires datetime library
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{formatted_time} - Song: {song_name}, Message: {message}"

    # Save  to external txt log
    with open("songbook_log.txt", "a", encoding='utf-8') as log_file:
        log_file.write(log_entry + "\n")