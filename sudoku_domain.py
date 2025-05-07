import tkinter as tk
import time
import threading

from helper import generate_domain_array


def Ai_caller():
    time.sleep(2)
    sudoku_grid.replace_all_cells(cell_data)



def get_color(number):
    normalized_number = number / 9.0
    r = int(255 * normalized_number)
    g = int(255 * (1 - abs(normalized_number - 0.5) * 2))
    b = int(255 * (1 - normalized_number))
    return f'#{r:02x}{g:02x}{b:02x}'


class SudokuDomain:
    def __init__(self, root, cell_data):
        self.root = root
        self.cells = []
        self.create_grid(cell_data)

    def create_grid(self, cell_data):
        for i in range(9):
            row = []
            for j in range(9):
                cell_value = cell_data[i][j]["value"]
                cell_color = "gray"
                if cell_data[i][j]["color"] == "white":
                    cell_value = cell_data[i][j]["domain"]
                    cell_color = get_color(len(cell_value))
                cell = tk.Frame(self.root, width=80, height=80, bg=cell_color, highlightbackground="black",
                                highlightthickness=1)
                cell.grid(row=i, column=j, padx=1, pady=1)
                label = tk.Label(cell, text="", font=('Arial', 12), justify='left')
                label.grid(row=0, column=0, padx=5, pady=5, sticky='nw')
                for k in range(0, len(cell_value), 3):
                    chunk = " ".join(map(str, cell_value[k:k + 3]))
                    label.config(text=label.cget("text") + chunk)
                    if k + 3 < len(cell_value):
                        label.config(text=label.cget("text") + "\n")
                row.append({"frame": cell, "label": label, "value": cell_value, "color": cell_color})  # Ensure "value" key is included
            self.cells.append(row)

    # Set an array for any cell (does not update the rest of cells)
    def update_cell(self, row, col, new_value):
        cell = self.cells[row][col]
        cell['label'].config(text="")
        for k in range(0, len(new_value), 3):
            chunk = " ".join(map(str, new_value[k:k + 3]))
            cell['label'].config(text=cell['label'].cget("text") + chunk)
            if k + 3 < len(new_value):
                cell['label'].config(text=cell['label'].cget("text") + "\n")
        cell_color = "gray"
        if self.cells[row][col]['color'] != "gray":
            cell_color = get_color(len(new_value))
        cell['frame'].config(bg=cell_color)
        self.root.update_idletasks()  # Update the display immediately

    # Use it to make an assumption for any cell (updates the rest of the cells automatic)
    def assign_digit(self, row, col, digit):
        # Assign the digit to the specified cell position
        self.cells[row][col]["value"] = [digit]

        # Remove the digit from all other cells in the same row
        for j in range(9):
            if j != col and digit in self.cells[row][j]["value"]:
                self.cells[row][j]["value"].remove(digit)
                self.update_cell(row, j, self.cells[row][j]["value"])

        # Remove the digit from all other cells in the same column
        for i in range(9):
            if i != row and digit in self.cells[i][col]["value"]:
                self.cells[i][col]["value"].remove(digit)
                self.update_cell(i, col, self.cells[i][col]["value"])

        # Remove the digit from all other cells in the same segment
        segment_row = row // 3
        segment_col = col // 3
        for i in range(segment_row * 3, segment_row * 3 + 3):
            for j in range(segment_col * 3, segment_col * 3 + 3):
                if i != row and j != col and digit in self.cells[i][j]["value"]:
                    self.cells[i][j]["value"].remove(digit)
                    self.update_cell(i, j, self.cells[i][j]["value"])

        # Update the cell with the assigned digit
        self.update_cell(row, col, [digit])

    def replace_all_cells(self, new_cell_data):
        for i in range(9):
            for j in range(9):
                new_value = new_cell_data[i][j]["value"]
                cell_color = "gray"
                if new_cell_data[i][j]["color"] == "white":
                    new_value = new_cell_data[i][j]["domain"]
                    cell_color = get_color(len(new_value))
                cell = self.cells[i][j]["frame"]
                label = self.cells[i][j]["label"]
                label.config(text="")
                for k in range(0, len(new_value), 3):
                    chunk = " ".join(map(str, new_value[k:k + 3]))
                    label.config(text=label.cget("text") + chunk)
                    if k + 3 < len(new_value):
                        label.config(text=label.cget("text") + "\n")
                cell_color = "gray"
                if new_cell_data[i][j]['color'] != "gray":
                    cell_color = get_color(len(new_value))
                cell.config(bg=cell_color)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sudoku Domains")
    root.geometry("500x700")  # Larger window size

    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    # Sample cell data
    cell_data = generate_domain_array(puzzle)

    sudoku_grid = SudokuDomain(root, cell_data)

    # Update a cell's value and color (e.g., cell at row 1, column 1)

    # Create and start a new thread to execute commands
    # thread = threading.Thread(target=Ai_caller)  # execute the algorithm and call update dynamically
    # thread.start()


    # sudoku_grid.update_cell(1, 1, [1, 2, 3, 4, 5, 8, 9])

    root.mainloop()
