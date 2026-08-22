import customtkinter as ctk
import main_generator
import threading
import subprocess


def get_git_status():
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return result.stdout.strip()

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

def update_songbook():
    update_button.configure(
        state="disabled",
        text="⏳  BUDUJĘ ŚPIEWNIK..."
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
    update_button.configure(
        state="normal",
        text="🔄  AKTUALIZUJ ŚPIEWNIK"
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
    update_button.configure(
        state="normal",
        text="🔄  AKTUALIZUJ ŚPIEWNIK"
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
    report_window.geometry("600x400")

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

def commit_and_push():
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
        height=45
    )
    confirm_button.pack(pady=15)

    cancel_button = ctk.CTkButton(
        confirmation_window,
        text="ANULUJ",
        command=confirmation_window.destroy,
        width=250
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
        width=150
    )
    button.pack(pady=20)

app = ctk.CTk()
app.title("IloSongbook 2.1")
app.geometry("600x400")


title_label = ctk.CTkLabel(
    app,
    text="ILO SONGBOOK",
    font=("Arial", 28, "bold")
)
title_label.pack(pady=40)


update_button = ctk.CTkButton(
    app,
    text="🔄  AKTUALIZUJ ŚPIEWNIK",
    command=update_songbook,
    width=280,
    height=50
)
update_button.pack(pady=20)

git_button = ctk.CTkButton(
    app,
    text="POKAŻ ZMIANY GIT",
    command=show_git_changes,
    width=280,
    height=40
)
git_button.pack(pady=10)

commit_button = ctk.CTkButton(
    app,
    text="COMMIT & PUSH",
    command=commit_and_push,
    width=280,
    height=40
)
commit_button.pack(pady=10)

status_label = ctk.CTkLabel(
    app,
    text="Gotowy"
)
status_label.pack(pady=10)


details_label = ctk.CTkLabel(
    app,
    text=""
)
details_label.pack(pady=10)


app.mainloop()