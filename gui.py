import customtkinter as ctk
import main_generator
import threading
import subprocess

# =========================
# ILO SONGBOOK – COLOR THEME
# =========================

BG_COLOR = "#08090B"
PANEL_COLOR = "#111316"
BUTTON_COLOR = "#0B0D0F"

NEON_RED = "#E52B32"
NEON_RED_DARK = "#64171B"

TEXT_MAIN = "#F0F0F0"
TEXT_SECONDARY = "#A8A8A8"


def get_git_status():
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return result.stdout.strip()

def get_git_branch():
    result=subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, encoding="utf-8")
    return result.stdout.strip()

def is_content_branch():
    return get_git_branch()== "main"

def run_git_command(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    if result.returncode != 0:
        raise Exception(
            result.stderr.strip() or "Polecenie Git zakończyło się błędem."
        )

    return result.stdout.strip()

def pull_latest():

    if has_local_changes():
        raise Exception(
            "LOCAL CHANGES DETECTED / Wykryto lokalne zmiany\n\n"
            "Finish or publish you current work before downloading updates.\n\n"
            "Zakończ lub opublikuj bieżące zmiany przed pobraniem aktualizacji." 
        )
    run_git_command(["git", "fetch", "upstream"])
    run_git_command(["git", "merge", "upstream/main"])

def has_local_changes():
    return bool(get_git_status())

def start_pull_latest():

    thread = threading.Thread(
        target=run_pull_latest,
        daemon=True
    )

    thread.start()


def run_pull_latest():

    try:
        pull_latest()

        app.after(
            0,
            show_git_message,
            "✓ UPDATED / ZAKTUALIZOWANO",
            "Repository is up to date.\n\n"
            "Repozytorium jest aktualne."
        )

    except Exception as error:

        app.after(
            0,
            show_git_message,
            "🔴 UPDATE ERROR / BŁĄD AKTUALIZACJI",
            str(error)
        )

def update_branch_info():
    branch = get_git_branch()

    if branch == "main":
        branch_label.configure(
            text="● MAIN / GŁÓWNA GAŁĄŹ",
            text_color=NEON_RED
        )
    else:
        branch_label.configure(
            text=f"⚠ {branch} / TRYB DEWELOPERSKI",
            text_color="#C98A8A"
        )

def update_songbook():
    set_dual_button(
        update_button,
        "⏳ BUILDING SONGBOOK...", 
        " Buduję śwpiewnik...",
        enabled=False
    )

    status_label.configure(
        text="Przetwarzanie..."
    )

    details_label.configure(
        text=""
    )

    thread = threading.Thread(
        target=run_build,
        daemon=True
    )

    thread.start()


def run_build():
    try:
        result = main_generator.build_songbook()

        app.after(
            0,
            show_build_result,
            result
        )

    except Exception as error:
        app.after(
            0,
            show_build_error,
            error
        )


def show_build_result(result):
    set_dual_button(update_button, 
        "UPDATE SONGBOOK", 
        "Aktualizuj śpiewnik", 
        enabled=True
    )
    git_status = get_git_status()

    if result["success"]:
        status_label.configure(
            text="✓ ŚPIEWNIK ZAKTUALIZOWANY"
        )
    else:
        status_label.configure(
            text="⚠ BUILD NIE ZAKOŃCZYŁ SIĘ POPRAWNIE"
        )

    if git_status:
        git_text = "● ZMIANY W REPOZYTORIUM"
    else:
        git_text = "● REPOZYTORIUM CZYSTE"

    details_label.configure(
        text=(
            f"Aktywne: {result['active']}\n"
            f"Archiwum: {result['archive']}\n"
            f"Testowe: {result['test']}\n"
            f"Ostrzeżenia: {len(result['warnings'])}\n"
            f"Błędy: {len(result['errors'])}\n\n"
            f"{git_text}"
        )
    
    )


def show_build_error(error):
    set_dual_button(update_button, 
            "UPDATE SONGBOOK", 
            "Aktualizuj śpiewnik", 
            enabled=True
        )

    status_label.configure(
        text="🔴 BŁĄD PODCZAS BUDOWANIA"
    )

    details_label.configure(
        text=str(error)
    )

def show_git_changes():
    git_status = get_git_status()

    if git_status:
        message = git_status
    else:
        message = "Brak niezacommitowanych zmian."

    report_window = ctk.CTkToplevel(app)
    report_window.title("Zmiany w repozytorium")
    report_window.geometry("600x450")
    report_window.transient(app)
    report_window.grab_set()
    report_window.focus_force()

    label = ctk.CTkLabel(
        report_window,
        text="GIT STATUS",
        font=("Arial", 22, "bold")
    )
    label.pack(pady=20)

    text_box = ctk.CTkTextbox(
        report_window,
        width=520,
        height=280
    )
    text_box.pack(padx=20, pady=10)

    text_box.insert("1.0", message)
    text_box.configure(state="disabled")

    ok_button = ctk.CTkButton(
        report_window,
        text="OK",
        command=report_window.destroy,
        width=150,
        height=35,
        fg_color=BUTTON_COLOR,
        hover_color="#15171A",
        border_color=NEON_RED,
        border_width=2,
        text_color=TEXT_MAIN
    )
    ok_button.pack(pady=15)

def commit_and_push():

    if not is_content_branch():
        show_git_message(
            "⚠ DEVELOPMENT BRANCH",
            (
                "You are not on the main branch.\n\n"
                "This tool is intended for songbook content updates only.\n\n"
                "Nie jesteś na głównej gałęzi.\n\n"
                "To narzędzie służy wyłącznie do aktualizacji "
                "treści śpiewnika.\n\n"
                "For code changes, use a development branch "
                "and merge it into main after testing."
            )
        )
        return

    git_status = get_git_status()

    if not git_status:
        show_git_message(
            "Brak zmian",
            "Repozytorium jest już aktualne."
        )
        return

    confirmation_window = ctk.CTkToplevel(app)
    confirmation_window.title("Potwierdzenie publikacji")
    confirmation_window.geometry("650x500")
    confirmation_window.transient(app)
    confirmation_window.grab_set()
    confirmation_window.focus_force()


    title = ctk.CTkLabel(
        confirmation_window,
        text="📤 PUBLIKACJA ZMIAN",
        font=("Arial", 24, "bold")
    )
    title.pack(pady=20)

    info = ctk.CTkLabel(
        confirmation_window,
        text="Następujące zmiany zostaną zacommitowane:"
    )
    info.pack(pady=10)

    text_box = ctk.CTkTextbox(
        confirmation_window,
        width=560,
        height=250
    )
    text_box.pack(padx=20, pady=10)

    text_box.insert("1.0", git_status)
    text_box.configure(state="disabled")

    confirm_button = ctk.CTkButton(
        confirmation_window,
        text="✓  COMMIT & PUSH",
        command=lambda: perform_commit_and_push(
            confirmation_window
        ),
        width=250,
        height=45,
        fg_color=BUTTON_COLOR,
        hover_color="#15171A",
        border_color=NEON_RED,
        border_width=2,
        text_color=TEXT_MAIN
    )
    confirm_button.pack(pady=15)

    cancel_button = ctk.CTkButton(
        confirmation_window,
        text="ANULUJ",
        command=confirmation_window.destroy,
        width=250,
        fg_color=BUTTON_COLOR,
        hover_color="#15171A",
        border_color=NEON_RED,
        border_width=2,
        text_color=TEXT_MAIN
    )
    cancel_button.pack()

def perform_commit_and_push(window):
    try:
        run_git_command(["git", "add", "-A"])

        commit_message = "Update songbook"

        run_git_command(
            ["git", "commit", "-m", commit_message]
        )

        run_git_command(["git", "push"])
        # print("TEST: tutaj nastąpił by git push")

        window.destroy()

        show_git_message(
            "✓ Opublikowano",
            "Zmiany zostały zacommitowane i wysłane do repozytorium."
        )

    except Exception as error:
        show_git_message(
            "🔴 Błąd Git",
            str(error)
        )

def show_git_message(title, message):
    message_window = ctk.CTkToplevel(app)
    message_window.title(title)
    message_window.geometry("500x300")
    message_window.transient(app)
    message_window.grab_set()
    message_window.focus_force()

    label = ctk.CTkLabel(
        message_window,
        text=message,
        wraplength=420,
        font=("Arial", 16)
    )
    label.pack(expand=True, padx=30, pady=30)

    button = ctk.CTkButton(
        message_window,
        text="OK",
        command=message_window.destroy,
        width=150,
        fg_color=BUTTON_COLOR,
        hover_color="#15171A",
        border_color=NEON_RED,
        border_width=2,
        text_color=TEXT_MAIN
    )
    button.pack(pady=20)

ctk.set_appearance_mode('dark')
app = ctk.CTk()
app.title("IloSongbook 2.1")
app.geometry("600x650")


title_label = ctk.CTkLabel(
    app,
    text="ILO SONGBOOK",
    font=("Arial", 28, "bold")
)
title_label.pack(pady=40)

def create_dual_button(parent, english, polish, command):
    button = ctk.CTkFrame(
        parent,
        fg_color=BUTTON_COLOR,
        border_color=NEON_RED,
        border_width=2,
        corner_radius=8,
        width=280,
        height=60
    )

    button.pack_propagate(False)

    button.english_label = ctk.CTkLabel(
        button,
        text=english,
        text_color=TEXT_MAIN,
        font=("Arial", 16, "bold")
    )
    button.english_label.pack(pady=(7, 0))

    button.polish_label = ctk.CTkLabel(
        button,
        text=polish,
        text_color=TEXT_SECONDARY,
        font=("Arial", 11, "italic")
    )
    button.polish_label.pack(pady=(0, 4))

    button.enabled = True

    def click(event):
        if button.enabled:
            command()


    def hover_on(event):
        if button.enabled:
            button.configure(
                border_color=NEON_RED,
                fg_color="#15171A"
            )


    def hover_off(event):
        if button.enabled:
            button.configure(
                border_color=NEON_RED_DARK,
                fg_color=BUTTON_COLOR
            )


    button.bind("<Button-1>", click)
    button.english_label.bind("<Button-1>", click)
    button.polish_label.bind("<Button-1>", click)

    button.bind("<Enter>", hover_on)
    button.bind("<Leave>", hover_off)

    button.english_label.bind("<Enter>", hover_on)
    button.english_label.bind("<Leave>", hover_off)

    button.polish_label.bind("<Enter>", hover_on)
    button.polish_label.bind("<Leave>", hover_off)

    return button

def set_dual_button(button, english=None, polish=None, enabled=True):
    button.enabled = enabled

    if english is not None:
        button.english_label.configure(text=english)

    if polish is not None:
        button.polish_label.configure(text=polish)

    if enabled:
        button.configure(
            border_color=NEON_RED,
            fg_color=BUTTON_COLOR
        )
        button.english_label.configure(
            text_color=TEXT_MAIN
        )
        button.polish_label.configure(
            text_color=TEXT_SECONDARY
        )
    else:
        button.configure(
            border_color=NEON_RED_DARK,
            fg_color="#08090B"
        )
        button.english_label.configure(
            text_color="#666666"
        )
        button.polish_label.configure(
            text_color="#444444"
        )

pull_button = create_dual_button (
    app,
    "GET LATEST VERSION",
    "Pobierz aktualną wersję",
    start_pull_latest
)
pull_button.pack (pady=10)

update_button = create_dual_button(
    app,
    "UPDATE SONGBOOK", 
    "Aktualizuj śpiewnik",
    update_songbook,
)
update_button.pack(pady=20)

git_button = create_dual_button(
    app,
    "SHOW GIT CHANGES",
    "Pokaż zmiany Git",
    show_git_changes
)
git_button.pack(pady=10)

commit_button = create_dual_button(
    app,
    "COMMIT & PUSH",
    "Zapisz i opublikuj",
    commit_and_push
)
commit_button.pack(pady=10)

status_label = ctk.CTkLabel(
    app,
    text="Gotowy"
)
status_label.pack(pady=10)

branch_label = ctk.CTkLabel(app, text="", font=("Arial", 12))
branch_label.pack(pady=(0,5))

scope_label = ctk.CTkLabel(
    app,
    text=(
        "CONTENT TOOL / NARZĘDZIE DO OBSŁUGI TREŚCI\n"
        "Use for songbook content updates only / "
        "Służy wyłącznie do aktualizacji treści śpiewnika"
    ),
    text_color=TEXT_SECONDARY,
    font=("Arial", 10, "italic"),
    justify="center"
)
scope_label.pack(pady=(5, 10))


details_label = ctk.CTkLabel(
    app,
    text=""
)
details_label.pack(pady=10)

update_branch_info()

app.mainloop()