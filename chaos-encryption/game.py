from GOL import GameOfLife
import tkinter as tk
import json

class GameOfLifeGUI:
    def __init__(self, root, length, width, tick_delay = None):
        self.root = root
        self.length = length
        self.width = width
        self.starting_cells = set()
        self.button_size = 1
        self.game = None
        
        self.tick_delay = 1000
        if(tick_delay):
            self.tick_delay = tick_delay

        self.create_grid()

    def create_grid(self):
        self.buttons = {}
        self.button_fonts = {}

        for row in range(self.length):
            for col in range(self.width):
                btn = tk.Button(self.root, width=self.button_size * 2, height=self.button_size,
                                command=lambda r=row, c=col: self.on_button_click(r, c))
                btn.grid(row=row, column=col, padx=0, pady=0)
                self.buttons[(row, col)] = btn

        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
        self.start_button.grid(row=self.length, column=0, columnspan=self.width, pady=10)

        self.zoom_in_button = tk.Button(self.root, text="Zoom In", command=lambda: self.zoom(1.5))
        self.zoom_in_button.grid(row=self.length + 1, column=0, columnspan=self.width // 2, pady=5)

        self.zoom_out_button = tk.Button(self.root, text="Zoom Out", command=lambda: self.zoom(0.5))
        self.zoom_out_button.grid(row=self.length + 1, column=self.width // 2, columnspan=self.width // 2, pady=5)

    def on_button_click(self, row, col):
        if (row, col) in self.starting_cells:
            self.starting_cells.remove((row, col))
            self.buttons[(row, col)].configure(bg="white")
        else:
            self.starting_cells.add((row, col))
            self.buttons[(row, col)].configure(bg="black")

    def disable_buttons(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button) and widget != self.start_button:
                widget.config(state="disabled")

    def set_white_cells(self):
        for button in self.buttons.values():
            button.config(bg="white")

    def set_black_cells(self, black_cells):
        for (row, col) in black_cells:
            self.buttons[(row, col)].config(bg="black")

    def start_game(self):
        self.game = GameOfLife(self.length, self.width, self.starting_cells)
        # self.game.set_game_moore()
        self.disable_buttons()
        self.update_game()

    def update_game(self):
        if not self.game:
            return

        black_cells = self.game.get_next_alive_cells()
        if black_cells:
            self.set_white_cells()
            self.set_black_cells(black_cells)
            self.root.after(self.tick_delay, self.update_game)

    def zoom(self, scale):
        print(f"zoom scale: {scale}")
        self.button_size = max(1, int(self.button_size * scale))
        print(self.button_size)
        for (row, col), button in self.buttons.items():
            button.config(width=self.button_size * 2, height=self.button_size)

        self.start_button.config(font=("TkDefaultFont", max(8, int(10 * scale))))
        self.zoom_in_button.config(font=("TkDefaultFont", max(8, int(10 * scale))))
        self.zoom_out_button.config(font=("TkDefaultFont", max(8, int(10 * scale))))

def main():
    length, width = 38, 38

    root = tk.Tk()
    root.title("Game of Life")
    game_gui = GameOfLifeGUI(root, length, width, 20)
    root.mainloop()

if __name__ == "__main__": 
    main()