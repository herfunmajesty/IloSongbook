# IloSongbook - Krakow Ukulele Tuesdays Songbook

A static songbook generator for the **Krakow Ukulele Tuesdays** community. It reads song files written in a simple text format, parses metadata and inline chords, and generates a full set of HTML pages ready to be hosted on GitHub Pages.

Live site: [ukulelekrakow.pl](https://ukulelekrakow.pl)

## Progressive Web App (PWA) & Offline Use

The songbook is a **Progressive Web App (PWA)** that can be installed directly onto smartphones, tablets, or computers to use offline during meetups and jam sessions.

When opened online, the Service Worker automatically caches the core app shell, chord diagrams, and the entire active song catalogue in the background. Once cached, lyrics, chord charts, search/filtering, and auto-scroll work completely without an internet connection.

### How to Install

- **Android (Chrome / Edge / Firefox)**:
  1. Open [ukulelekrakow.pl](https://ukulelekrakow.pl).
  2. Tap the browser menu (**⋮**) or the install prompt at the bottom of the screen.
  3. Tap **Install app** (or **Add to Home screen**).
- **iOS / iPadOS (Safari)**:
  1. Open [ukulelekrakow.pl](https://ukulelekrakow.pl) in Safari.
  2. Tap the **Share** button (the square with an upward arrow).
  3. Scroll down and select **Add to Home Screen**, then tap **Add**.
- **Desktop (Chrome / Edge / Brave)**:
  1. Open [ukulelekrakow.pl](https://ukulelekrakow.pl).
  2. Click the **Install** icon in the browser address bar (or select *Install Krakow Ukulele...* from the menu).


## How It Works

`main_generator.py` reads `.txt` song files from three directories, processes them through Jinja2 HTML templates, and outputs a browsable songbook website into the `out/` directory.

### Song Collections

| Collection | Input directory | Output directory | Description |
|---|---|---|---|
| **Active** | `in/songs/active/` | `out/` | Main songbook — songs played at meetups |
| **Archive** | `in/songs/archive/` | `out/archive/` | Retired or seasonal songs |
| **New / Test** | `in/songs/new/` | `out/new/` | Songs being prepared or tested |

Each collection is sorted alphabetically, numbered, and rendered into individual song pages and a song list page.

## Song File Format

Each song is a `.txt` file. The filename should match the song title (e.g. `Hotel California.txt`).

### Metadata Header

Metadata is defined at the top of the file using `{key:value}` syntax:

```
{t:Song Title}
{artist:Artist Name}
{level:Easy}
{spotify:spotify_track_id}
{youtube:youtube_video_id}
{d:4}
```

| Key | Required | Description |
|---|---|---|
| `t` | Yes | Song title. Prefix with `🔥` for new songs, `⭐` / `🎂` / `🎅` for special tags |
| `artist` | Yes | Artist or band name |
| `level` | Yes | Difficulty: `Easy`, `Medium`, or `Hard` |
| `spotify` | No | Spotify track ID (used for linking) |
| `youtube` | No | YouTube video ID |
| `d` | No | Song duration in minutes (default: `4`), used for auto-scroll |

### Lyrics and Chords

Chords are written inline within square brackets directly in the lyrics:

```
[G] Love is a [C/] burning [G] thing
[G] And it makes a [C/] fiery [G] ring
```

- Append `/` to a chord for a single strum, e.g. `[C/]`
- Use `[stop]`, `[muted]`, `[riff]` for performance annotations
- Use `[back]...[/back]` for background vocal lines
- Use `<grey>...</grey>` for muted/optional text
- Section labels use HTML: `<small><i>(Chorus)</i></small>`
- Tablature can be included inside `<pre>...</pre>` blocks
- HTML comments `<!-- -->` can be used for internal notes

### Example

```
{t:Ring Of Fire}
{artist:Johnny Cash}
{level:Easy}
{spotify:6YffUZJ2R06kyxyK6onezL}

Intro:
[G] pa pa ra pa ra [C/] pa ra [G] paaaa

[G] Love is a [C/] burning [G] thing
[G] And it makes a [C/] fiery [G] ring
```

## Project Structure

```
IloSongbook/
├── main_generator.py          # Main generator script
├── songbook_log.txt           # Auto-generated processing log
├── CNAME                      # Custom domain config for GitHub Pages
├── in/
│   ├── songs/
│   │   ├── active/            # Active songbook songs (.txt)
│   │   ├── archive/           # Archived songs (.txt)
│   │   └── new/               # New/test songs (.txt)
│   ├── template/
│   │   ├── index.html         # Landing page template
│   │   ├── song.html          # Song page template (active)
│   │   ├── song_hidden.html   # Song page template (archive/new)
│   │   ├── songs.html         # Song list template (active)
│   │   ├── songs_hidden.html  # Song list template (archive/new)
│   │   ├── manifest.json      # PWA Web App Manifest
│   │   └── sw.js              # Service Worker template (offline caching)
│   ├── chords/                # Ukulele chord diagram images (.gif)
│   └── images/                # Logos, icons, PWA app icons (icon-192, icon-512)
└── out/                       # Generated HTML output (do not edit)
    ├── index.html
    ├── songs.html
    ├── manifest.json          # Copied PWA manifest
    ├── sw.js                  # Generated Service Worker with pre-cache list
    ├── *.html                 # Individual song pages
    ├── archive/               # Archived song pages
    ├── new/                   # New/test song pages
    ├── chords/                # Copied chord diagrams
    └── images/                # Copied images and app icons
```

## Requirements

- Python 3
- [Jinja2](https://pypi.org/project/Jinja2/)

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

With the virtual environment activated, run the generator from the project root:

```bash
python main_generator.py
```

This will:

1. Copy images, icons, and chord diagrams from `in/` to `out/`
2. Copy non-rendered files (`how.html`, `manifest.json`, `CNAME`) to `out/`
3. Read and parse all song files from the three song directories
4. Validate song titles and metadata (results logged to `songbook_log.txt`)
5. Generate individual HTML pages for each song
6. Generate song list pages for each collection
7. Generate the index page
8. Generate `out/sw.js` with full pre-caching metadata for offline PWA operation

The output in `out/` is then deployed to GitHub Pages.

## Deployment

The site is deployed automatically via GitHub Pages using the workflow in `.github/workflows/static.yml`. The custom domain `ukulelekrakow.pl` is configured through the `CNAME` file.
