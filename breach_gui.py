import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# Importiere deine Module
from snipping import SnippingTool
from cv2_tmm import detect_breach_protocol_data
from breach_hack import solve_breach_protocol, format_solution

class BreachProtocolGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Breach Protocol Solver")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.matrix_grid = None
        self.sequence_grid = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Breach Protocol Solver", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Einstellungen", padding="5")
        settings_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        settings_frame.columnconfigure(1, weight=1)
        
        # Buffer size setting
        ttk.Label(settings_frame, text="Buffer Größe:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.buffer_var = tk.StringVar(value="8")
        buffer_spinbox = ttk.Spinbox(settings_frame, from_=4, to=12, width=10, 
                                   textvariable=self.buffer_var, state="readonly")
        buffer_spinbox.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Buttons
        self.main_btn = ttk.Button(button_frame, text="🚀 Screenshot & Lösen", 
                                  command=self.run_full_process)
        self.main_btn.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        self.reset_btn = ttk.Button(button_frame, text="🔄 Zurücksetzen", 
                                   command=self.reset_process)
        self.reset_btn.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Console output frame
        console_frame = ttk.LabelFrame(main_frame, text="Konsolen-Ausgabe", padding="5")
        console_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        # Console text widget with scrollbar
        self.console_text = scrolledtext.ScrolledText(console_frame, height=20, width=80,
                                                     font=("Consolas", 10), 
                                                     bg="black", fg="green",
                                                     insertbackground="green")
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear console button
        clear_btn = ttk.Button(console_frame, text="🗑️ Konsole leeren", 
                              command=self.clear_console)
        clear_btn.grid(row=1, column=0, pady=(5, 0), sticky=tk.W)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit - Klicke auf 'Screenshot aufnehmen' um zu starten")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Initial console message
        self.write_to_console("=== Breach Protocol Solver gestartet ===\n")
        self.write_to_console("1. Stelle die gewünschte Buffer-Größe ein (Standard: 8)\n")
        self.write_to_console("2. Klicke auf 'Screenshot & Lösen' um den kompletten Prozess zu starten\n")
        self.write_to_console("3. Wähle den Bereich aus und das Programm löst automatisch das Puzzle\n\n")
        
    def write_to_console(self, text):
        """Schreibt Text in die Konsole"""
        self.console_text.insert(tk.END, text)
        self.console_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_console(self):
        """Leert die Konsole"""
        self.console_text.delete(1.0, tk.END)
        
    def update_status(self, text):
        """Aktualisiert die Statusleiste"""
        self.status_var.set(text)
        self.root.update_idletasks()
        
    def run_full_process(self):
        """Führt den kompletten Prozess aus: Screenshot -> Analyse -> Lösung"""
        def full_process():
            try:
                # Schritt 1: Screenshot
                self.update_status("Screenshot-Modus aktiv - Wähle einen Bereich aus")
                self.write_to_console("\n🚀 KOMPLETTER PROZESS GESTARTET\n")
                self.write_to_console("="*50 + "\n")
                self.write_to_console("📷 Schritt 1/3: Screenshot aufnehmen...\n")
                
                # Deaktiviere Button während des Prozesses
                self.main_btn.config(state="disabled")
                
                # Minimiere das Hauptfenster
                self.root.withdraw()
                
                # Starte Snipping Tool
                snipping_tool = SnippingTool()
                snipping_tool.run()
                
                # Stelle das Hauptfenster wieder her
                self.root.deiconify()
                self.root.lift()
                
                self.write_to_console("✅ Screenshot erfolgreich aufgenommen!\n\n")
                
                # Schritt 2: Analyse
                self.update_status("Analysiere Screenshot...")
                self.write_to_console("🔍 Schritt 2/3: Analysiere Screenshot...\n")
                
                # Capture stdout/stderr für die Konsole
                console_output = io.StringIO()
                
                with redirect_stdout(console_output), redirect_stderr(console_output):
                    # Erkenne Matrix und Sequenzen
                    self.matrix_grid, self.sequence_grid = detect_breach_protocol_data(
                        screenshot_path='screenshot/screenshot.png',
                        hex_images_path="hexcodes",
                        threshold=0.8,
                        visualize=False
                    )
                
                # Zeige die gesammelten Ausgaben
                output = console_output.getvalue()
                if output:
                    self.write_to_console(output)
                
                if not self.matrix_grid or not self.sequence_grid:
                    self.write_to_console("❌ Keine Matrix oder Sequenzen erkannt!\n")
                    self.write_to_console("Überprüfe ob:\n")
                    self.write_to_console("- Der Screenshot den richtigen Bereich zeigt\n")
                    self.write_to_console("- Die Hex-Templates vorhanden sind\n")
                    self.update_status("Analyse fehlgeschlagen")
                    messagebox.showerror("Analysefehler", "Keine Matrix oder Sequenzen erkannt!")
                    return
                
                self.write_to_console(f"✅ Matrix erkannt: {len(self.matrix_grid)} x {len(self.matrix_grid[0])}\n")
                self.write_to_console(f"✅ Sequenzen erkannt: {len(self.sequence_grid)}\n")
                
                # Zeige erkannte Daten
                self.write_to_console("\nErkannte Matrix:\n")
                for i, row in enumerate(self.matrix_grid):
                    self.write_to_console(f"Zeile {i}: {' '.join(row)}\n")
                
                self.write_to_console("\nErkannte Sequenzen:\n")
                for i, seq in enumerate(self.sequence_grid):
                    self.write_to_console(f"Sequenz {i+1}: {' '.join(seq)}\n")
                
                # Schritt 3: Lösung
                self.update_status("Löse Puzzle...")
                self.write_to_console(f"\n🧩 Schritt 3/3: Löse Puzzle...\n")
                
                # Löse das Puzzle
                try:
                    buffer_size = int(self.buffer_var.get())
                except ValueError:
                    buffer_size = 8
                    self.write_to_console(f"⚠️ Ungültige Buffer-Größe, verwende Standard: {buffer_size}\n")
                
                self.write_to_console(f"Buffer-Größe: {buffer_size}\n")
                result = solve_breach_protocol(self.matrix_grid, self.sequence_grid, buffer_size)
                
                if result:
                    self.write_to_console("🎉 LÖSUNG GEFUNDEN! 🎉\n\n")
                    solution_text = format_solution(result, self.matrix_grid)
                    self.write_to_console(solution_text)
                    self.write_to_console("\n" + "="*50 + "\n")
                    
                    # Zeige auch eine kurze Zusammenfassung
                    sequence_str = ' '.join(result['sequence'])
                    path_str = ' -> '.join([f"({x},{y})" for x, y in result['path']])
                    
                    self.write_to_console(f"\n📋 ZUSAMMENFASSUNG:\n")
                    self.write_to_console(f"Eingabe-Sequenz: {sequence_str}\n")
                    self.write_to_console(f"Pfad: {path_str}\n")
                    self.write_to_console(f"Abgedeckte Sequenzen: {len(result['covered_sequences'])}/{len(self.sequence_grid)}\n")
                    self.write_to_console(f"\n🏆 PROZESS ERFOLGREICH ABGESCHLOSSEN! 🏆\n")
                    
                    self.update_status("✅ Puzzle erfolgreich gelöst!")
                    
                    # Zeige Erfolgs-Dialog
                    messagebox.showinfo("Lösung gefunden!", 
                                      f"Das Puzzle wurde automatisch gelöst!\n\n"
                                      f"Sequenz: {sequence_str}\n"
                                      f"Schritte: {len(result['sequence'])}\n"
                                      f"Abgedeckt: {len(result['covered_sequences'])}/{len(self.sequence_grid)} Sequenzen")
                else:
                    self.write_to_console("❌ Keine Lösung gefunden!\n")
                    self.write_to_console("Das Puzzle kann mit den gegebenen Parametern nicht gelöst werden.\n")
                    self.update_status("❌ Keine Lösung gefunden")
                    messagebox.showwarning("Keine Lösung", "Das Puzzle konnte nicht gelöst werden.")
                    
            except Exception as e:
                error_msg = f"❌ Fehler im Prozess: {str(e)}\n"
                self.write_to_console(error_msg)
                self.update_status("❌ Prozess-Fehler")
                messagebox.showerror("Prozess-Fehler", str(e))
                # Stelle das Hauptfenster wieder her falls ein Fehler auftritt
                self.root.deiconify()
            finally:
                # Aktiviere Button wieder
                self.main_btn.config(state="normal")
        
        # Starte in separatem Thread
        threading.Thread(target=full_process, daemon=True).start()
        
    def reset_process(self):
        """Setzt den Prozess zurück"""
        self.matrix_grid = None
        self.sequence_grid = None
        self.clear_console()
        self.write_to_console("=== Breach Protocol Solver zurückgesetzt ===\n")
        self.write_to_console("Bereit für einen neuen Durchlauf.\n\n")
        self.update_status("Zurückgesetzt - Bereit für neuen Screenshot")
        self.main_btn.config(state="normal")
        
    def run(self):
        """Startet die GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BreachProtocolGUI()
    app.run()