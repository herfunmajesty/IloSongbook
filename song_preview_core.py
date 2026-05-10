def convert_song_text_to_html(text, template_path):
    metadata = parse_song_metadata(text)

    title = metadata.get('t')
    artist = metadata.get('artist')
    level = metadata.get('level')
    spotify = metadata.get('spotify')
    youtube = metadata.get('youtube')
    duration = float(metadata.get('d', 4))

    lyrics_raw = re.sub(r"{.*?}", "", text)

    lyrics = lyrics_raw
    for old, new in replacements.items():
        lyrics = lyrics.replace(old, new)

    lyrics = remove_extra_empty_lines(lyrics)
    chords = extract_chords(lyrics_raw, "preview")

    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('song.html')

    html = template.render(
        title=title,
        artist=artist,
        number="PREVIEW",
        level=level,
        duration=duration,
        lyrics=lyrics,
        spotify=spotify,
        youtube=youtube,
        sticky=True,
        chords=chords,
        ltrans=Song.convert_level(level)
    )

    return html