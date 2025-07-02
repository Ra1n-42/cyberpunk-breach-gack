import cv2 as cv
import numpy as np
import os
from matplotlib import pyplot as plt

class BreachProtocolDetector:
    def __init__(self, screenshot_path='screenshot/screenshot.png', 
                 hex_images_path="hexcodes", threshold=0.8):
        self.screenshot_path = screenshot_path
        self.HEX_IMAGES_PATH = hex_images_path
        self.MATRIX = "/matrix/"
        self.SEQUENCE = "/sequence/"
        self.VALID_HEX_VALUES = ["55", "1C", "BD", "E9", "7A", "FF"]
        self.threshold = threshold
        
        # Initialize data
        self.matrix_grid = None
        self.sequence_grid = None
        self.screenshot = None
        self.output_img = None
        
    def load_screenshot(self):
        """Load screenshot in grayscale"""
        self.screenshot = cv.imread(self.screenshot_path, cv.IMREAD_GRAYSCALE)
        assert self.screenshot is not None, "Screenshot could not be loaded"
        
        # Convert to BGR for visualization
        self.output_img = cv.cvtColor(self.screenshot, cv.COLOR_GRAY2BGR)
        
    def build_grid(self, positions, row_threshold=15):
        """
        Build a 2D grid (list of lists) from detected positions.
        Positions format: [(x, y, code), ...]
        Sorted top-to-bottom, left-to-right.
        row_threshold defines max pixel difference to be in same row.
        """
        # Sort by y (top to bottom)
        positions = sorted(positions, key=lambda p: p[1])

        rows = []
        current_row = []
        last_y = None

        # Group into rows based on y threshold
        for pos in positions:
            x, y, code = pos
            if last_y is None or abs(y - last_y) <= row_threshold:
                current_row.append(pos)
            else:
                # sort current row by x (left to right)
                current_row.sort(key=lambda p: p[0])
                rows.append(current_row)
                current_row = [pos]
            last_y = y
        if current_row:
            current_row.sort(key=lambda p: p[0])
            rows.append(current_row)

        # Build the final grid of codes
        grid = []
        for row in rows:
            codes_row = [code for (_, _, code) in row]
            grid.append(codes_row)

        return grid

    def detect_hex_codes(self, base_img, valid_codes, templates_folder, offset=10):
        """
        Detect hex codes in base_img using templates from templates_folder.
        Returns list of (x, y, code) for detected positions.
        """
        found_positions = []
        for hex_code in valid_codes:
            template_path = os.path.join(templates_folder, f"{hex_code}.png")
            template = cv.imread(template_path, cv.IMREAD_GRAYSCALE)
            assert template is not None, f"Template {hex_code} could not be loaded from {template_path}"
            w, h = template.shape[::-1]

            res = cv.matchTemplate(base_img, template, cv.TM_CCOEFF_NORMED)
            loc = np.where(res >= self.threshold)

            for pt in zip(*loc[::-1]):
                # filter out points too close to existing detections
                if all(np.linalg.norm(np.array(pt) - np.array(pos[:2])) > offset for pos in found_positions):
                    found_positions.append((pt[0], pt[1], hex_code))

        return found_positions
    
    def detect_and_build_grids(self, visualize=False):
        """Main method to detect hex codes and build grids"""
        if self.screenshot is None:
            self.load_screenshot()
            
        # Generate colors for visualization
        np.random.seed(42)
        colors = {code: tuple(int(c) for c in np.random.randint(0, 255, 3)) for code in self.VALID_HEX_VALUES}
        
        # --- Detect MATRIX hex codes ---
        found_positions_matrix = self.detect_hex_codes(
            self.screenshot, self.VALID_HEX_VALUES, self.HEX_IMAGES_PATH + self.MATRIX
        )
        print(f"Detected {len(found_positions_matrix)} hex codes in MATRIX area.")

        # Draw MATRIX detections
        for x, y, code in found_positions_matrix:
            template_path = os.path.join(self.HEX_IMAGES_PATH + self.MATRIX, f"{code}.png")
            template = cv.imread(template_path, cv.IMREAD_GRAYSCALE)
            w, h = template.shape[::-1]
            cv.rectangle(self.output_img, (x, y), (x + w, y + h), colors[code], 2)
            cv.putText(self.output_img, "M:" + code, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, colors[code], 1, cv.LINE_AA)

        self.matrix_grid = self.build_grid(found_positions_matrix)
        print("MATRIX GRID:")
        for row in self.matrix_grid:
            print(row)

        # --- Detect SEQUENCE hex codes ---
        found_positions_sequence = self.detect_hex_codes(
            self.screenshot, self.VALID_HEX_VALUES, self.HEX_IMAGES_PATH + self.SEQUENCE
        )
        print(f"Detected {len(found_positions_sequence)} hex codes in SEQUENCE area.")

        # Draw SEQUENCE detections (different color - e.g. white)
        for x, y, code in found_positions_sequence:
            template_path = os.path.join(self.HEX_IMAGES_PATH + self.SEQUENCE, f"{code}.png")
            template = cv.imread(template_path, cv.IMREAD_GRAYSCALE)
            w, h = template.shape[::-1]
            # Use a fixed color for SEQUENCE (e.g., white)
            cv.rectangle(self.output_img, (x, y), (x + w, y + h), (255, 255, 255), 2)
            cv.putText(self.output_img, "S:" + code, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv.LINE_AA)

        self.sequence_grid = self.build_grid(found_positions_sequence)
        print("SEQUENCE GRID:")
        for row in self.sequence_grid:
            print(row)
            
        # Show visualization if requested
        if visualize:
            self.show_detections()
            
        return self.matrix_grid, self.sequence_grid
    
    def show_detections(self):
        """Show all detections using matplotlib"""
        plt.figure(figsize=(15, 10))
        plt.imshow(cv.cvtColor(self.output_img, cv.COLOR_BGR2RGB))
        plt.title("Detected Hex Codes: MATRIX (colors) & SEQUENCE (white)")
        plt.axis('off')
        plt.show()
    
    def get_matrix(self):
        """Get the detected matrix grid"""
        if self.matrix_grid is None:
            self.detect_and_build_grids()
        return self.matrix_grid
    
    def get_sequences(self):
        """Get the detected sequence grid"""
        if self.sequence_grid is None:
            self.detect_and_build_grids()
        return self.sequence_grid

# Convenience functions for backward compatibility and easy import
def detect_breach_protocol_data(screenshot_path='images/breach_protocol_screenshot.png', 
                               hex_images_path="hexcodes", threshold=0.8, visualize=False):
    """
    Convenience function to detect and return matrix and sequences
    Returns: (matrix_grid, sequence_grid)
    """
    detector = BreachProtocolDetector(screenshot_path, hex_images_path, threshold)
    return detector.detect_and_build_grids(visualize=visualize)

# For direct execution (backward compatibility)
if __name__ == "__main__":
    # Paths and constants
    screenshot_path = 'images/breach_protocol_screenshot.png'
    HEX_IMAGES_PATH = "hexcodes"
    
    # Detect and display
    matrix_grid, sequence_grid = detect_breach_protocol_data(
        screenshot_path, HEX_IMAGES_PATH, visualize=False
    )