from typing import List, Tuple, Dict
import numpy as np
# Import des Breach Protocol Detectors
from cv2_tmm import detect_breach_protocol_data

# Konstanten
HEXLIST = ["55", "1C", "BD", "E9", "7A", "FF"]
BUFFER_SIZE = 8

def solve_breach_protocol(matrix: List[List[str]], sequences: List[List[str]], buffer_size: int) -> Dict:
    y_len, x_len = len(matrix), len(matrix[0])
    best_solution = None
    target_sequences = len(sequences)

    def contains_sequence(main: List[str], sub: List[str]) -> bool:
        """Prüft, ob eine Teilsequenz in der Hauptsequenz enthalten ist."""
        for i in range(len(main) - len(sub) + 1):
            if main[i:i + len(sub)] == sub:
                return True
        return False

    def count_covered_sequences(sequence: List[str]) -> int:
        """Zählt die Anzahl der abgedeckten Sequenzen."""
        return sum(1 for seq in sequences if contains_sequence(sequence, seq))

    def backtrack(path: List[str], positions: List[Tuple[int, int]], used: List[List[bool]], 
                  step: int, current_x: int, current_y: int, move_horizontal: bool):
        nonlocal best_solution
        
        # Prüfe, ob alle Sequenzen abgedeckt sind
        covered_count = count_covered_sequences(path)
        if covered_count == target_sequences:
            # Wenn alle Sequenzen abgedeckt sind, prüfe ob dies die beste Lösung ist
            if best_solution is None or len(path) < len(best_solution['sequence']):
                covered = [seq for seq in sequences if contains_sequence(path, seq)]
                best_solution = {
                    'path': positions[:],
                    'sequence': path[:],
                    'covered_sequences': covered
                }
                return  # Früher Ausstieg, da wir eine optimale Lösung für diese Pfadlänge gefunden haben
        
        # Stoppe, wenn Puffergröße erreicht
        if step >= buffer_size:
            return
        
        # Pruning: Wenn wir bereits eine Lösung haben und der aktuelle Pfad schon länger ist, stoppe
        if best_solution and len(path) >= len(best_solution['sequence']):
            return

        if move_horizontal:
            # Bewege dich horizontal (y bleibt gleich, x ändert sich)
            for new_x in range(x_len):
                if new_x != current_x and not used[current_y][new_x]:
                    value = matrix[current_y][new_x]
                    new_path = path + [value]
                    new_positions = positions + [(new_x, current_y)]
                    new_used = [row[:] for row in used]
                    new_used[current_y][new_x] = True
                    backtrack(new_path, new_positions, new_used, step + 1, new_x, current_y, False)
        else:
            # Bewege dich vertikal (x bleibt gleich, y ändert sich)
            for new_y in range(y_len):
                if new_y != current_y and not used[new_y][current_x]:
                    value = matrix[new_y][current_x]
                    new_path = path + [value]
                    new_positions = positions + [(current_x, new_y)]
                    new_used = [row[:] for row in used]
                    new_used[new_y][current_x] = True
                    backtrack(new_path, new_positions, new_used, step + 1, current_x, new_y, True)

    # Starte in Zeile 0 (erste Zeile), wähle eine beliebige Spalte
    for start_col in range(x_len):
        used = [[False] * x_len for _ in range(y_len)]
        used[0][start_col] = True
        value = matrix[0][start_col]
        path = [value]
        positions = [(start_col, 0)]
        # Nach dem ersten Schritt bewegen wir uns vertikal (move_horizontal = False)
        backtrack(path, positions, used, 1, start_col, 0, False)

    return best_solution

def format_solution(result: Dict, matrix: List[List[str]]) -> str:
    """Formatiert die Lösung mit der Matrix und Schrittnummern."""
    if not result:
        return "Keine Lösung gefunden."
    
    path = result['path']
    sequence = result['sequence']
    covered = result['covered_sequences']
    
    # Erstelle eine Kopie der Matrix für die Ausgabe
    y_len, x_len = len(matrix), len(matrix[0])
    display_matrix = [[f"{matrix[y][x]}" for x in range(x_len)] for y in range(y_len)]
    
    # Füge Schrittnummern zu den Positionen im Pfad hinzu
    for step, (x, y) in enumerate(path, 1):
        display_matrix[y][x] = f"{matrix[y][x]}({step})"
    
    # Formatiere die Matrix für die Ausgabe
    matrix_str = "Matrix mit Schritten:\n"
    for row in display_matrix:
        matrix_str += " ".join(f"{val:8}" for val in row) + "\n"
    
    # Formatiere den Pfad und die Sequenzen
    path_str = " -> ".join([f"({x},{y})" for x, y in path])
    seq_str = ", ".join([" ".join(seq) for seq in covered])
    return (
        f"{matrix_str}\n"
        f"Optimale Sequenz: {' '.join(sequence)}\n"
        f"Lösungspfad: {path_str}\n"
        f"Abgedeckte Sequenzen: {seq_str}"
    )

def main():
    print("=== Breach Protocol Detector ===")
    print("Lade Screenshot und erkenne Hex-Codes...")
    
    try:
        # Erkenne Matrix und Sequenzen automatisch
        matrix_grid, sequence_grid = detect_breach_protocol_data(
            screenshot_path='screenshot/screenshot.png',
            hex_images_path="hexcodes",
            threshold=0.8,
            visualize=False  # Setze auf True, wenn du die Visualisierung sehen möchtest
        )
        
        print(f"\nErkannte Matrix: {len(matrix_grid)} x {len(matrix_grid[0]) if matrix_grid else 0}")
        print(f"Erkannte Sequenzen: {len(sequence_grid)}")
        
        if not matrix_grid or not sequence_grid:
            print("Fehler: Keine Matrix oder Sequenzen erkannt!")
            return
        
        print("\n=== Löse Breach Protocol ===")
        result = solve_breach_protocol(matrix_grid, sequence_grid, BUFFER_SIZE)
        
        if result:
            print(format_solution(result, matrix_grid))
        else:
            print("Keine Lösung gefunden!")
            
    except FileNotFoundError as e:
        print(f"Fehler: Datei nicht gefunden - {e}")
        print("Stelle sicher, dass:")
        print("1. Das Screenshot unter 'images/breach_protocol_screenshot.png' existiert")
        print("2. Die Hex-Templates unter 'hexcodes/matrix/' und 'hexcodes/sequence/' existieren")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")

if __name__ == "__main__":
    main()