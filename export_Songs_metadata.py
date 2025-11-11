import os
import re
import csv
import urllib.parse

def parse_song_metadata(text):
    """Zwraca metadane piosenki jako słownik."""
    metadata_pattern = r"\{(.*?):(.*?)\}"
    matches = re.findall(metadata_pattern, text)
    return {key.strip(): value.strip() for key, value in matches}

def extract_chords(text):
    """Zwraca listę unikalnych akordów z tekstu piosenki."""
    chords_pattern = r"\[([A-G][^/\]\s]*)\]"  # dopasowanie [Am], [G7], [Cmaj7] itd.
    chords = re.findall(chords_pattern, text)
    # filtrowanie nietypowych znaczników (np. [stop], [riff])
    chords = [c for c in chords if c.lower() not in ['riff', 'stop', 'solo', 'nc', 'muted', 'back']]
    return sorted(set(chords))

def detect_sections(text):
    """Analizuje obecność sekcji (Verse, Chorus, Bridge itp.) i ich format."""
    part_tag_pattern = r"\((verse|chorus|bridge|intro|outro|interlude)\)"
    has_parts = bool(re.search(part_tag_pattern, text, re.IGNORECASE))

    # Czy są otagowane np. <small><i> lub <i>
    if "<small><i>" in text:
        part_format = "<small><i>"
    elif "<i>" in text:
        part_format = "<i>"
    else:
        part_format = "none"

    return has_parts, part_format

def export_metadata_to_csv(base_dir, output_csv):
    """
    Eksportuje metadane piosenek do pliku TSV (tabulatorowy CSV) z kolumną 'edit_link'
    zawierającą ścieżkę otwierającą plik .txt do edycji.
    """
    songs_data = []
    subfolders = ["active", "archive", "new"]

    # 🧠 Jeśli plik już istnieje, zapytaj o nadpisanie
    if os.path.exists(output_csv):
        print(f"⚠️  Plik {output_csv} już istnieje.")
        confirm = input("Czy na pewno chcesz go NADPISAĆ? (t/n): ").strip().lower()
        if confirm not in ("t", "tak", "y", "yes"):
            print("❌ Eksport przerwany – plik nie został zmieniony.")
            return
        print("✅ Kontynuuję – stary plik zostanie zastąpiony.\n")

    for sub in subfolders:
        folder_path = os.path.join(base_dir, sub)
        if not os.path.exists(folder_path):
            continue

        for filename in os.listdir(folder_path):
            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            metadata = parse_song_metadata(content)

            # detekcja elementów dodatkowych
            has_info = ("info" in content.lower()) or ('<span class="mark fw-bold">' in content)
            has_riff = ('[riff]' in content.lower()) or ('<pre>' in content.lower())
            has_parts, part_format = detect_sections(content)
            chords = extract_chords(content)
            is_new = "🔥" in metadata.get("t", "")

            # 🔗 Link do edycji pliku (file:///...)
            abs_path = os.path.abspath(file_path)
            # 🧩 Ścieżka w formacie Windows z podwójnymi backslashami
            excel_path = abs_path.replace("/", "\\")
            # 📎 Formuła Excela w języku polskim
            file_url = f'=HIPERŁĄCZE("{excel_path}";"otwórz plik")'

            songs_data.append({
                "folder": sub,
                "file_name": filename,
                "title": metadata.get("t", ""),
                "artist": metadata.get("artist", ""),
                "level": metadata.get("level", ""),
                "spotify": metadata.get("spotify", ""),
                "youtube": metadata.get("youtube", ""),
                "duration": metadata.get("d", ""),
                "sticky": "True",
                "is_new": is_new,
                "has_info": has_info,
                "part_tags": has_parts,
                "part_format": part_format,
                "chord_count": len(chords),
                "chord_list": ", ".join(chords),
                "has_riff": has_riff,
                "edit_link": file_url
            })

    # 💾 Zapis do pliku TSV (tabulatorowy CSV)
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "folder", "file_name", "title", "artist", "level",
            "spotify", "youtube", "duration", "sticky",
            "is_new", "has_info", "part_tags", "part_format",
            "chord_count", "chord_list", "has_riff",
            "edit_link"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(songs_data)

    print(f"💾 Zapisano {len(songs_data)} piosenek do {output_csv}")
    print("🔗 Kolumna 'edit_link' umożliwia otwarcie pliku .txt do edycji z poziomu Excela / Calc.")

if __name__ == "__main__":
    base_dir = os.path.join(os.getcwd(), "in", "songs")
    output_csv = "songs_metadata.csv"
    export_metadata_to_csv(base_dir, output_csv)