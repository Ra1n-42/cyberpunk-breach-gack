import tkinter as tk
import pyautogui

SCREENSHOT_PATH = "./screenshot/"
NAME = "screenshot.png"
HEXCODES = "./hexcodes/"
MATRIX = HEXCODES + "matrix/"
SEQUENCE = HEXCODES + "sequence/"

class SnippingTool:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.rect = None

        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)  # Fenster leicht transparent
        self.root.configure(background='black')
        self.root.bind("<Button-1>", self.on_click)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.on_release)
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def on_click(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        # Rechteck initialisieren
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_drag(self, event):
        cur_x, cur_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        # Rechteck während Ziehen aktualisieren
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.root.destroy()  # GUI schließen

        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)
        width, height = x2 - x1, y2 - y1

        # Screenshot des ausgewählten Bereichs
        screenshot = pyautogui.screenshot(region=(int(x1), int(y1), int(width), int(height)))

        screenshot.save(SCREENSHOT_PATH + NAME)
        print(f"Screenshot gespeichert: " + NAME)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    SnippingTool().run()
