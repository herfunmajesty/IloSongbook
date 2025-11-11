import os
import re
import csv
import shutil
import datetime

# ==============================
# 🔧 KONFIGURACJA
# ==============================
VALID_LEVELS = {"Easy", "Medium", "Hard"}
DRY_RUN = False   # 🔸 ustaw False, gdy chcesz naprawdę zapisać zmiany
BASE_DIR = os.path.join(os.getcwd(), "in", "songs")
CSV_PATH = "songs_metadata.csv"

# 📁 Ścieżka do kopii zapasowych (poza projektem)
BACKUP_ROOT = r"G:\SongbookBackups"
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
BACKUP_FOLDER = os.path.join(BACKUP_ROOT, TIMESTAMP)
# ==============================


def update_song_file(file_path, updates, relative_folder):
    """Podmienia lub dodaje metadane w pliku tekstowym na podstawie słownika `updates`."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False
    for key, new_value in updates.items():
        if not new_value:
            continue

        pattern = r"\{" + re.escape(key) + r":.*?\}"
        replacement = f"{{{key}:{new_value}}}"
        new_content, count = re.subn(pattern, replacement, content)

        if count > 0 and new_content != content:
            content = new_content
            modified = True
            print(f"   🔸 Zmieniono {key} → {new_value}")
        elif count == 0:
            print(f"   ➕ Dodano brakujące pole {{{key}:{new_value}}}")
            content = replacement + "\n" + content
            modified = True

    if modified:
        if DRY_RUN:
            print("   💡 (dry run) zmiana nie została zapisana")
        else:
            # 🔹 Tworzenie folderu backupu na dysku G
            backup_dir = os.path.join(BACKUP_FOLDER, relative_folder)
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))

            shutil.copy(file_path, backup_path)
            print(f"   💾 Kopia zapisana: {backup_path}")

            # 🔹 Nadpisanie oryginalnego pliku po wykonaniu backupu
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)


def update_songs_from_csv(base_dir, csv_path):
    """Aktualizuje wszystkie pliki txt na podstawie CSV."""
    # automatyczne rozpoznanie separatora (tab, przecinek, średnik)
    with open(csv_path, 'r', encoding='utf-8') as test_file:
        sample = test_file.read(1024)
        if '\t' in sample:
            delimiter = '\t'
        elif ';' in sample:
            delimiter = ';'
        else:
            delimiter = ','
    print(f"📑 Wykryty separator CSV: {repr(delimiter)}")

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        print(f"Nagłówki w CSV: {reader.fieldnames}")

        for row in reader:
            target_folder = row["folder"].strip()
            filename = row["file_name"].strip()

            # znajdź faktyczny folder pliku
            actual_folder = None
            for possible in ["active", "archive", "new"]:
                candidate = os.path.join(base_dir, possible, filename)
                if os.path.exists(candidate):
                    actual_folder = possible
                    file_path = candidate
                    break

            if actual_folder is None:
                print(f"⚠️ Plik {filename} nie został znaleziony w żadnym folderze, pomijam.")
                continue

            print(f"\n🎵 {filename} ({actual_folder} → {target_folder})")

            updates = {
                "t": row["title"].strip(),
                "artist": row["artist"].strip(),
                "level": row["level"].strip() if row["level"].strip() in VALID_LEVELS else None,
                "spotify": row["spotify"].strip(),
                "youtube": row["youtube"].strip(),
                "d": row["duration"].strip(),
            }

            update_song_file(file_path, updates, actual_folder)

            # jeśli folder się zmienił — przenosimy
            if target_folder != actual_folder and target_folder in ["active", "archive", "new"]:
                new_path = os.path.join(base_dir, target_folder, filename)
                print(f"   📦 Przeniesienie: {actual_folder} → {target_folder}")
                if not DRY_RUN:
                    os.makedirs(os.path.join(base_dir, target_folder), exist_ok=True)
                    shutil.move(file_path, new_path)
                else:
                    print("   💡 (dry run) plik nie został przeniesiony")


if __name__ == "__main__":
    print(f"\n🚀 Startuję aktualizację plików z {CSV_PATH}")
    print(f"Tryb: {'DRY RUN (podgląd zmian)' if DRY_RUN else 'ZAPIS RZECZYWISTY'}")
    print(f"Kopie zapasowe będą w: {BACKUP_FOLDER}\n")

    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    update_songs_from_csv(BASE_DIR, CSV_PATH)

    print("\n🎉 Aktualizacja zakończona.")