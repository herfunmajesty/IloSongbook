"""
ILO Songbook Editor - MVP

Co robi:
- otwiera plik .txt z piosenką,
- pozwala edytować treść w oknie,
- pokazuje metadane i wykryte akordy,
- ma przyciski do szybkiego wstawiania akordów i typowych znaczników,
- generuje preview HTML na bazie szablonu song.html,
- otwiera preview w przeglądarce.

Wymagania:
- Python 3.x
- pip install jinja2
- plik song.html w tym samym folderze co ten skrypt

Uruchomienie:
    py songbook_editor.py
"""

from __future__ import annotations

import os
import re
import tempfile
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    Environment = None
    FileSystemLoader = None


# ============================================================
# CORE - logika zgodna z Twoim songbookiem
# ============================================================

REPLACEMENTS = {
    "<grey>": "<span class='text-muted'>",
    "</grey>": "</span>",
    "<info>": "<div class=\"alert alert-warning mb-1 song-info-box\">",
    "</info>": "</div>",
    "<ex>": "<span class=\"extra-hint\">",
    "</ex>": "</span>",
    "[stop]": "<strong>[stop]</strong>",
    "[muted]": "<strong>[muted]</strong>",
    "[riff]": "<span class='text-muted'><strong>(riff)</strong></span>",
    "[back]": "<b><i>",
    "[/back]": "</b></i>",
    "[": "<span class=\"chord\">[",
    "]": "]</span>",
    "<d>": "<span style=\"color: purple;\"><small><i>",
    "</d>": "</i></small></span>",
    "<r>": "<small><b>",
    "</r>": "</b></small>",
    "<s>": "<small><i>",
    "</s>": "</i></small>",
    "\n": "<br>",
}

REQUIRED_METADATA = ["d", "spotify", "t", "artist", "level"]
OPTIONAL_METADATA = ["youtube"]

LEVEL_TO_BOOTSTRAP = {
    "Easy": "success",
    "Medium": "warning",
    "Hard": "danger",
}


@dataclass
class ParsedSong:
    metadata: Dict[str, str]
    lyrics_html: str
    chords: List[str]
    warnings: List[str]


def parse_song_metadata(text: str) -> Dict[str, str]:
    metadata_pattern = r"\{(.*?):(.*?)\}"
    metadata_matches = re.findall(metadata_pattern, text)
    return {key.strip(): value.strip() for key, value in metadata_matches}


def normalize_chord(chord: str) -> str:
    return chord.replace("\\", "").replace("/", "").replace("#", "sharp").strip()


def extract_chords(text: str) -> List[str]:
    chords_pattern = r"\[(.*?)\]"
    chords_matches = re.findall(chords_pattern, text)

    chords_list: List[str] = []
    seen = set()
    ignored_keywords = ["riff", "stop", "solo", "back", "pause", "muted", "nc"]

    for match in chords_matches:
        lowered = match.lower().strip()
        if any(keyword in lowered for keyword in ignored_keywords):
            continue

        normalized = normalize_chord(match)
        if not normalized:
            continue

        # Obsługa zroślaków typu [Am F C G]
        parts = normalized.split() if " " in normalized else [normalized]
        for part in parts:
            if part and part not in seen:
                seen.add(part)
                chords_list.append(part)

    return chords_list


def remove_extra_empty_lines_from_html_breaks(text: str, max_empty_lines: int = 1) -> str:
    # Po zamianie \n na <br> pilnujemy, żeby nie robić wielkich pustych bloków.
    lines = re.split(r"<br\s*/?>|\n", text)
    new_lines = []
    empty_count = 0

    for line in lines:
        if line.strip() == "":
            empty_count += 1
        else:
            empty_count = 0

        if empty_count <= max_empty_lines:
            new_lines.append(line)

    return "<br>".join(new_lines)


def convert_lyrics_to_html(raw_lyrics: str) -> str:
    lyrics = raw_lyrics
    for old, new in REPLACEMENTS.items():
        lyrics = lyrics.replace(old, new)
    return remove_extra_empty_lines_from_html_breaks(lyrics)


def validate_song_text(text: str) -> List[str]:
    warnings: List[str] = []
    metadata = parse_song_metadata(text)

    for key in REQUIRED_METADATA:
        if not metadata.get(key):
            warnings.append(f"Brak wymaganej metadanej: {{{key}:...}}")

    level = metadata.get("level")
    if level and level not in LEVEL_TO_BOOTSTRAP:
        warnings.append(f"Nietypowy level: {level}. Oczekiwane: Easy / Medium / Hard")

    title = metadata.get("t", "")
    if title and "\n" in title:
        warnings.append("Tytuł wygląda podejrzanie - sprawdź metadane {t:...}")

    # Prosty check HTML-owych markerów pomocniczych
    for tag in ["s", "d", "r", "grey", "info", "ex"]:
        open_count = text.count(f"<{tag}>")
        close_count = text.count(f"</{tag}>")
        if open_count != close_count:
            warnings.append(f"Niezamknięty albo nadmiarowy znacznik: <{tag}> / </{tag}>")

    # Zapisy stare / do migracji
    deprecated_checks = [
        ("<small><i>", "Stary zapis <small><i>... użyj <s>...</s>"),
        ("</i></small>", "Stary zapis </i></small> - sprawdź i zamień na </s>"),
        ("<b class=\"mark\">", "Stary zapis mark - rozważ <r>...</r> albo <info>...</info>"),
        ("class=\"mark", "Stary zapis class=mark - rozważ <r>...</r> albo <info>...</info>"),
        ("<span class=\"mark", "Stary zapis span mark - rozważ <info>...</info>"),
    ]
    for needle, message in deprecated_checks:
        if needle in text:
            warnings.append(message)

    if re.search(r"(?im)^\s*info\s*:", text):
        warnings.append("Stary zapis 'info:' - rozważ <info>...</info>")

    if re.search(r"\[[^\]\n]*\\[^\]\n]*\]", text):
        warnings.append("Podejrzany/stary zapis akordu z backslashem, np. [A\\] - sprawdź standard")

    return warnings


def parse_song(text: str) -> ParsedSong:
    metadata = parse_song_metadata(text)
    raw_lyrics = re.sub(r"\{.*?\}", "", text, flags=re.DOTALL)
    chords = extract_chords(raw_lyrics)
    lyrics_html = convert_lyrics_to_html(raw_lyrics)
    warnings = validate_song_text(text)
    return ParsedSong(metadata=metadata, lyrics_html=lyrics_html, chords=chords, warnings=warnings)


def render_song_html(text: str, template_file: Path) -> str:
    if Environment is None or FileSystemLoader is None:
        raise RuntimeError("Brakuje biblioteki jinja2. Zainstaluj: py -m pip install jinja2")

    parsed = parse_song(text)
    meta = parsed.metadata

    title = meta.get("t", "PREVIEW - brak tytułu")
    artist = meta.get("artist", "")
    level = meta.get("level", "")
    duration_raw = meta.get("d", "4")

    try:
        duration = float(duration_raw)
    except ValueError:
        duration = 4.0

    template_dir = template_file.parent
    template_name = template_file.name

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template(template_name)

    html = template.render(
        title=title,
        artist=artist,
        number="PREVIEW",
        level=level,
        duration=duration,
        lyrics=parsed.lyrics_html,
        spotify=meta.get("spotify"),
        youtube=meta.get("youtube"),
        sticky=True,
        chords=parsed.chords,
        ltrans=LEVEL_TO_BOOTSTRAP.get(level, "secondary"),
    )
    return html


# ============================================================
# GUI
# ============================================================

class SongbookEditor(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ILO Songbook Editor - MVP")
        self.geometry("1200x760")
        self.minsize(980, 620)

        self.current_file: Optional[Path] = None
        self.template_file: Path = Path(__file__).with_name("song.html")
        self.preview_file: Path = Path(tempfile.gettempdir()) / "ilo_song_preview.html"

        self._build_ui()
        self._bind_shortcuts()
        self.refresh_analysis()

    # ---------------- UI ----------------

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=8)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(8, weight=1)

        ttk.Button(top, text="Otwórz .txt", command=self.open_file).grid(row=0, column=0, padx=3)
        ttk.Button(top, text="Zapisz", command=self.save_file).grid(row=0, column=1, padx=3)
        ttk.Button(top, text="Zapisz jako", command=self.save_file_as).grid(row=0, column=2, padx=3)
        ttk.Button(top, text="Preview HTML", command=self.preview_html).grid(row=0, column=3, padx=12)
        ttk.Button(top, text="Wybierz song.html", command=self.choose_template).grid(row=0, column=4, padx=3)
        ttk.Button(top, text="Odśwież analizę", command=self.refresh_analysis).grid(row=0, column=5, padx=3)

        self.file_label = ttk.Label(top, text="Brak pliku")
        self.file_label.grid(row=0, column=8, sticky="e", padx=8)

        main = ttk.PanedWindow(self, orient="horizontal")
        main.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # Lewy panel - edytor
        editor_frame = ttk.Frame(main)
        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)

        self.text = tk.Text(
            editor_frame,
            wrap="word",
            undo=True,
            font=("Consolas", 11),
            padx=10,
            pady=10,
        )
        self.text.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(editor_frame, command=self.text.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scroll.set)

        main.add(editor_frame, weight=4)

        # Prawy panel - narzędzia
        side = ttk.Frame(main, padding=8)
        side.columnconfigure(0, weight=1)
        side.rowconfigure(4, weight=1)
        main.add(side, weight=2)

        meta_box = ttk.LabelFrame(side, text="Metadane", padding=8)
        meta_box.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        meta_box.columnconfigure(1, weight=1)

        self.meta_labels: Dict[str, ttk.Label] = {}
        for idx, key in enumerate(["t", "artist", "level", "d", "key", "spotify", "youtube"]):
            ttk.Label(meta_box, text=f"{key}:").grid(row=idx, column=0, sticky="w")
            value = ttk.Label(meta_box, text="—", wraplength=300)
            value.grid(row=idx, column=1, sticky="w")
            self.meta_labels[key] = value

        chord_box = ttk.LabelFrame(side, text="Akordy piosenki", padding=8)
        chord_box.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        chord_box.columnconfigure(0, weight=1)

        chord_controls = ttk.Frame(chord_box)
        chord_controls.grid(row=0, column=0, sticky="ew")
        ttk.Label(chord_controls, text="Tryb:").pack(side="left")
        self.chord_mode = tk.StringVar(value="normal")
        ttk.Radiobutton(chord_controls, text="[A]", variable=self.chord_mode, value="normal").pack(side="left")
        ttk.Radiobutton(chord_controls, text="[A/]", variable=self.chord_mode, value="slash").pack(side="left")
        ttk.Radiobutton(chord_controls, text="[A] ...", variable=self.chord_mode, value="dots").pack(side="left")
        ttk.Radiobutton(chord_controls, text="[A/] ...", variable=self.chord_mode, value="slash_dots").pack(side="left")

        manual = ttk.Frame(chord_box)
        manual.grid(row=1, column=0, sticky="ew", pady=(6, 6))
        manual.columnconfigure(0, weight=1)
        self.manual_chords_var = tk.StringVar(value="")
        self.manual_chords: List[str] = []
        ttk.Entry(manual, textvariable=self.manual_chords_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(manual, text="Ustaw", command=self.set_manual_chords).grid(row=0, column=1, padx=(4, 0))

        self.chord_buttons_frame = ttk.Frame(chord_box)
        self.chord_buttons_frame.grid(row=2, column=0, sticky="ew")

        snippets_box = ttk.LabelFrame(side, text="Formuły / znaczniki", padding=8)
        snippets_box.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self._build_snippet_buttons(snippets_box)

        transform_box = ttk.LabelFrame(side, text="Transformacje zaznaczenia", padding=8)
        transform_box.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(transform_box, text="Akordy → slash", command=self.selection_chords_to_slash).grid(row=0, column=0, sticky="ew", pady=2)
        ttk.Button(transform_box, text="Akordy → normalne", command=self.selection_chords_to_normal).grid(row=1, column=0, sticky="ew", pady=2)
        ttk.Button(transform_box, text="Owiń <s>...</s>", command=lambda: self.wrap_selection("<s>", "</s>")).grid(row=2, column=0, sticky="ew", pady=2)
        ttk.Button(transform_box, text="Owiń <r>...</r>", command=lambda: self.wrap_selection("<r>", "</r>")).grid(row=3, column=0, sticky="ew", pady=2)
        ttk.Button(transform_box, text="Owiń <d>...</d>", command=lambda: self.wrap_selection("<d>", "</d>")).grid(row=4, column=0, sticky="ew", pady=2)

        warnings_box = ttk.LabelFrame(side, text="Walidacja", padding=8)
        warnings_box.grid(row=4, column=0, sticky="nsew")
        warnings_box.rowconfigure(0, weight=1)
        warnings_box.columnconfigure(0, weight=1)
        self.warnings = tk.Text(warnings_box, height=8, wrap="word", font=("Segoe UI", 9))
        self.warnings.grid(row=0, column=0, sticky="nsew")
        self.warnings.configure(state="disabled")

        bottom = ttk.Frame(self, padding=(8, 0, 8, 8))
        bottom.grid(row=2, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="Gotowe")
        ttk.Label(bottom, textvariable=self.status_var).grid(row=0, column=0, sticky="w")

        self.text.bind("<<Modified>>", self._on_text_modified)

    def _build_snippet_buttons(self, parent: ttk.Frame) -> None:
        snippets = [
            ("Intro", "<s>(Intro)</s>\n"),
            ("Verse", "<s>(Verse)</s>\n"),
            ("Chorus", "<s>(Chorus)</s>\n"),
            ("Bridge", "<s>(Bridge)</s>\n"),
            ("Instrumental", "<s>(Instrumental)</s>\n"),
            ("Outro", "<s>(Outro)</s>\n"),
            ("INFO box", "<info>\nBeats per chord: \nStrumming: \n</info>\n"),
            ("Hint / EX", "<ex></ex>"),
            ("stop", "[stop]"),
            ("muted", "[muted]"),
            ("riff", "[riff]"),
            ("back on", "[back]"),
            ("back off", "[/back]"),
            ("grey", "<grey></grey>"),
        ]
        for i, (label, value) in enumerate(snippets):
            row = i // 3
            col = i % 3
            ttk.Button(parent, text=label, command=lambda v=value: self.insert_at_cursor(v)).grid(
                row=row, column=col, sticky="ew", padx=2, pady=2
            )
            parent.columnconfigure(col, weight=1)

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-o>", lambda _e: self.open_file())
        self.bind("<Control-s>", lambda _e: self.save_file())
        self.bind("<F5>", lambda _e: self.preview_html())
        self.bind("<Control-r>", lambda _e: self.refresh_analysis())

    # ---------------- File actions ----------------

    def open_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Wybierz plik piosenki",
            filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")],
        )
        if not path:
            return
        self.current_file = Path(path)
        text = self.current_file.read_text(encoding="utf-8")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text)
        self.text.edit_modified(False)
        self.file_label.configure(text=str(self.current_file))
        self.status_var.set(f"Otwarty plik: {self.current_file.name}")
        self.refresh_analysis()

    def save_file(self) -> None:
        if self.current_file is None:
            self.save_file_as()
            return
        self.current_file.write_text(self.get_text(), encoding="utf-8")
        self.text.edit_modified(False)
        self.status_var.set(f"Zapisano: {self.current_file.name}")
        self.refresh_analysis()

    def save_file_as(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Zapisz piosenkę jako",
            defaultextension=".txt",
            filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")],
        )
        if not path:
            return
        self.current_file = Path(path)
        self.save_file()
        self.file_label.configure(text=str(self.current_file))

    def choose_template(self) -> None:
        path = filedialog.askopenfilename(
            title="Wybierz szablon song.html",
            filetypes=[("HTML", "*.html"), ("Wszystkie pliki", "*.*")],
        )
        if not path:
            return
        self.template_file = Path(path)
        self.status_var.set(f"Wybrano szablon: {self.template_file.name}")

    # ---------------- Preview and analysis ----------------

    def preview_html(self) -> None:
        try:
            if not self.template_file.exists():
                messagebox.showerror(
                    "Brak szablonu",
                    f"Nie znaleziono szablonu:\n{self.template_file}\n\nWłóż song.html obok skryptu albo wybierz go przyciskiem.",
                )
                return
            html = render_song_html(self.get_text(), self.template_file)
            self.preview_file.write_text(html, encoding="utf-8")
            webbrowser.open(self.preview_file.as_uri())
            self.status_var.set(f"Preview wygenerowany: {self.preview_file}")
            self.refresh_analysis()
        except Exception as exc:
            messagebox.showerror("Błąd preview", str(exc))
            self.status_var.set("Błąd podczas generowania preview")

    def refresh_analysis(self) -> None:
        text = self.get_text()
        parsed = parse_song(text) if text.strip() else ParsedSong({}, "", [], ["Brak treści piosenki"])

        for key, label in self.meta_labels.items():
            label.configure(text=parsed.metadata.get(key, "—"))

        display_chords = self._merge_chords(parsed.chords, self.manual_chords)
        self._populate_chord_buttons(display_chords)
        self._write_warnings(parsed.warnings, parsed.chords)

    @staticmethod
    def _merge_chords(detected: List[str], manual: List[str]) -> List[str]:
        """Łączy akordy wykryte w tekście z ręcznie dodanymi, bez duplikatów."""
        merged: List[str] = []
        seen = set()
        for chord in list(detected) + list(manual):
            chord = chord.strip()
            if chord and chord not in seen:
                seen.add(chord)
                merged.append(chord)
        return merged

    def _write_warnings(self, warnings: List[str], chords: List[str]) -> None:
        self.warnings.configure(state="normal")
        self.warnings.delete("1.0", "end")

        if not warnings:
            self.warnings.insert("end", "✔ OK - brak oczywistych problemów\n")
        else:
            for item in warnings:
                self.warnings.insert("end", f"❌ {item}\n")

        self.warnings.insert("end", "\n")
        self.warnings.insert("end", f"Akordy wykryte: {', '.join(chords) if chords else '—'}\n")
        self.warnings.configure(state="disabled")

    def _populate_chord_buttons(self, chords: List[str]) -> None:
        for child in self.chord_buttons_frame.winfo_children():
            child.destroy()

        if not chords:
            ttk.Label(self.chord_buttons_frame, text="Brak wykrytych akordów").grid(row=0, column=0, sticky="w")
            return

        for i, chord in enumerate(chords):
            row = i // 4
            col = i % 4
            ttk.Button(
                self.chord_buttons_frame,
                text=chord,
                command=lambda c=chord: self.insert_chord(c),
            ).grid(row=row, column=col, sticky="ew", padx=2, pady=2)
            self.chord_buttons_frame.columnconfigure(col, weight=1)

    def set_manual_chords(self) -> None:
        raw = self.manual_chords_var.get().strip()
        new_chords = [c.strip() for c in re.split(r"[,;\s]+", raw) if c.strip()]

        # "Ustaw" ma DODAĆ ręczne akordy do tych już wykrytych w tekście,
        # a nie zastępować cały panel.
        self.manual_chords = self._merge_chords(self.manual_chords, new_chords)

        text = self.get_text()
        detected = parse_song(text).chords if text.strip() else []
        display_chords = self._merge_chords(detected, self.manual_chords)
        self._populate_chord_buttons(display_chords)

        self.status_var.set(
            f"Dodano ręczne akordy: {', '.join(new_chords) if new_chords else '—'}"
        )

    # ---------------- Text helpers ----------------

    def get_text(self) -> str:
        return self.text.get("1.0", "end-1c")

    def insert_at_cursor(self, value: str) -> None:
        # Hint / EX: jeśli jest zaznaczenie, owiń je zamiast wstawiać pusty tag.
        if value == "<ex></ex>":
            sel = self.get_selection(show_message=False)
            if sel is not None:
                start, end, selected = sel
                self.text.delete(start, end)
                self.text.insert(start, f"<ex>{selected}</ex>")
            else:
                self.text.insert("insert", value)
            self.text.focus_set()
            self.refresh_analysis()
            self.schedule_highlight()
            return

        self.text.insert("insert", value)
        self.text.focus_set()
        self.refresh_analysis()
        self.schedule_highlight()

    def insert_chord(self, chord: str) -> None:
        mode = self.chord_mode.get()
        if mode == "slash":
            value = f"[{chord}/]"
        elif mode == "dots":
            value = f"[{chord}] ..."
        elif mode == "slash_dots":
            value = f"[{chord}/] ..."
        else:
            value = f"[{chord}]"
        self.insert_at_cursor(value)

    def get_selection(self, show_message: bool = True) -> Optional[tuple[str, str, str]]:
        try:
            start = self.text.index("sel.first")
            end = self.text.index("sel.last")
            value = self.text.get(start, end)
            return start, end, value
        except tk.TclError:
            if show_message:
                messagebox.showinfo("Brak zaznaczenia", "Najpierw zaznacz fragment tekstu.")
            return None

    def replace_selection(self, new_value: str) -> None:
        sel = self.get_selection()
        if sel is None:
            return
        start, end, _value = sel
        self.text.delete(start, end)
        self.text.insert(start, new_value)
        self.refresh_analysis()

    def wrap_selection(self, prefix: str, suffix: str) -> None:
        sel = self.get_selection()
        if sel is None:
            return
        _start, _end, value = sel
        self.replace_selection(f"{prefix}{value}{suffix}")

    def selection_chords_to_slash(self) -> None:
        sel = self.get_selection()
        if sel is None:
            return
        _start, _end, value = sel

        def repl(match: re.Match[str]) -> str:
            chord = match.group(1).strip()
            if chord.endswith("/") or chord.endswith("..."):
                return f"[{chord}]"
            return f"[{chord}/]"

        self.replace_selection(re.sub(r"\[([^\]]+)\]", repl, value))

    def selection_chords_to_normal(self) -> None:
        sel = self.get_selection()
        if sel is None:
            return
        _start, _end, value = sel

        def repl(match: re.Match[str]) -> str:
            chord = match.group(1).strip()
            chord = chord.rstrip("/")
            chord = re.sub(r"\.\.\.$", "", chord)
            return f"[{chord}]"

        self.replace_selection(re.sub(r"\[([^\]]+)\]", repl, value))

    def _on_text_modified(self, _event=None) -> None:
        if self.text.edit_modified():
            self.status_var.set("Zmieniono treść - pamiętaj o zapisie")
            # Odświeżamy lekko po każdej zmianie. Przy bardzo dużych plikach można to wyłączyć.
            self.refresh_analysis()
            self.text.edit_modified(False)


def main() -> None:
    app = SongbookEditor()
    app.mainloop()


if __name__ == "__main__":
    main()
