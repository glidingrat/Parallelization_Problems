import tkinter as tk
import os
import subprocess
import threading
import sys

# Globální proces pro simulaci
current_process = None

def get_simulation_file(sim_type):
    """
    Vrací správnou cestu k souboru simulace na základě toho, zda aplikace běží jako exe.
    """
    if getattr(sys, 'frozen', False):  # Pokud běží jako .exe
        base_path = os.path.join(sys._MEIPASS, "src", "Parallelization_Problems")
    else:
        base_path = os.path.join(os.path.dirname(__file__), "Parallelization_Problems")

    path = os.path.join(base_path, f"{sim_type}.py")
    return path


def show_simulation(sim_type, title):
    """
    Zobrazí obrazovku simulace s daným typem simulace a názvem.
    Vyčistí předchozí widgety, nastaví název a vytvoří tlačítka a textové pole
    pro výstup simulace.

    Parametry:
    sim_type (str): Typ simulace (např. "Deadlock", "Livelock", "Starvation").
    title (str): Název okna simulace.
    """
    for widget in root.winfo_children():
        widget.destroy()

    root.title(title)

    # Nadpis
    tk.Label(root, text=f"{sim_type} Simulation", font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=10)

    # Textové pole pro výstup
    code_field = tk.Text(root, width=70, height=15, font=("Courier New", 10), wrap="word")
    code_field.pack(padx=10, pady=10)

    # Tlačítka
    button_frame = tk.Frame(root, bg="#f0f8ff")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Spustit simulaci", command=lambda: simulate(sim_type, code_field), bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=15)\
        .grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Zpět do menu", command=show_menu, bg="#f44336", fg="white", font=("Arial", 12, "bold"), width=15)\
        .grid(row=0, column=1, padx=10)


def simulate(sim_type, code_field):
    """
    Spustí vybranou simulaci a zobrazí výstup ve zvoleném textovém poli.
    Pokud již simulace běží, ukončí ji před spuštěním nové.

    Parametry:
    sim_type (str): Typ simulace, kterou chcete spustit (např. "Deadlock", "Livelock", "Starvation").
    code_field (tk.Text): Textové pole pro zobrazení výstupu simulace.
    """
    global current_process

    # Ukončí aktuální proces, pokud stále běží
    if current_process and current_process.poll() is None:
        current_process.terminate()
        current_process = None

    code_field.delete("1.0", "end")

    simulation_file = get_simulation_file(sim_type)

    if not os.path.exists(simulation_file):
        code_field.insert("end", f"Soubor {simulation_file} nebyl nalezen.\n")
        return

    def run_simulation():
        """
        Spustí simulaci v samostatném vlákně a zachytává její výstup.
        """
        global current_process
        try:
            current_process = subprocess.Popen(
                ["python", simulation_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            def read_output(pipe, tag):
                """
                Čte výstup ze zvoleného pipe a vkládá ho do textového pole.
                """
                for line in iter(pipe.readline, ''):
                    if code_field.winfo_exists():  # Kontrola, zda pole stále existuje
                        code_field.insert("end", f"{line}", tag)
                        code_field.see("end")
                pipe.close()

            stdout_thread = threading.Thread(target=read_output, args=(current_process.stdout, "stdout"))
            stderr_thread = threading.Thread(target=read_output, args=(current_process.stderr, "stderr"))

            stdout_thread.start()
            stderr_thread.start()
            stdout_thread.join()
            stderr_thread.join()

            if current_process and current_process.poll() is not None:  # Kontrola, zda proces skončil
                current_process.wait()
                if current_process.returncode != 0:
                    if code_field.winfo_exists():
                        code_field.insert("end",
                                          f"\nSimulace skončila s chybou (kód {current_process.returncode}).\n",
                                          "stderr")
                else:
                    if code_field.winfo_exists():
                        code_field.insert("end", "\nSimulace byla úspěšně dokončena.\n", "stdout")

        except Exception as e:
            if code_field.winfo_exists():
                code_field.insert("end", f"Došlo k chybě: {e}\n", "stderr")

    threading.Thread(target=run_simulation, daemon=True).start()


def show_menu():
    """
    Zobrazí hlavní menu s tlačítky pro výběr typu simulace.
    Ukončí jakoukoli probíhající simulaci před návratem do menu.
    """
    global current_process

    # Ukončení aktuálního procesu při návratu do menu
    if current_process and current_process.poll() is None:
        current_process.terminate()
        current_process = None

    for widget in root.winfo_children():
        widget.destroy()

    root.title("Parallelization Problems")

    menu_frame = tk.Frame(root, bg="#f0f8ff")
    menu_frame.pack(expand=True)

    # Nadpis
    tk.Label(menu_frame, text="Problémy Paralelizace", font=("Helvetica", 20, "bold"), bg="#f0f8ff").pack(pady=20)

    # Tlačítka
    buttons = [
        ("Deadlock", lambda: show_simulation("Deadlock", "Deadlock Simulation")),
        ("Livelock", lambda: show_simulation("Livelock", "Livelock Simulation")),
        ("Starvation", lambda: show_simulation("Starvation", "Starvation Simulation"))
    ]

    button_frame = tk.Frame(menu_frame, bg="#f0f8ff")
    button_frame.pack(pady=10)

    for i, (text, command) in enumerate(buttons):
        tk.Button(button_frame, text=text, command=command, font=("Arial", 14), bg="#2196F3", fg="white", width=20, height=2)\
            .grid(row=i, column=0, pady=10)


def center_window(window, width, height):
    """
    Vycentruje okno na obrazovce.

    Parametry:
    window (tk.Tk): Tkinter okno, které chcete vycentrovat.
    width (int): Šířka okna.
    height (int): Výška okna.
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


# Hlavní okno
root = tk.Tk()
center_window(root, 600, 400)
root.configure(bg="#f0f8ff")
root.resizable(False, False)
show_menu()

root.mainloop()
