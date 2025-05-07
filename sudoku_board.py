import tkinter as tk
from tkinter import messagebox
import time
import threading

from helper import generate_domain_array


class SudokuGameGui:
    def __init__(self, root, puzzle, sudoku_board, sudoku_domain=None, edit_block=False):
        self.root = root
        self.root.title("Sudoku")
        self.readonly = edit_block  # Flag to indicate if entries are readonly
        self.sol = puzzle
        self.create_grid(puzzle, sudoku_board)
        self.sudoku_domain = sudoku_domain

    def create_grid(self, puzzle, sudoku_board):
        def validate_input(char):
            if char.isdigit() and 1 <= int(char) <= 9:
                return True
            return False

        def enforce_char_limit(event):
            if self.readonly:
                return 'break'  # Prevent keyboard input if entries are readonly

            entry = event.widget
            if len(entry.get()) > 0:
                entry.delete(0, tk.END)
            if event.char.isdigit() and 1 <= int(event.char) <= 9:
                entry.insert(0, event.char)
            return 'break'

        def validate_row_col(event):
            if self.readonly:
                return False  # Prevent validation if entries are readonly

            entry = event.widget
            char = entry.get().strip()
            current_row, current_col = int(entry.grid_info()["row"]), int(entry.grid_info()["column"])

            # Check if the entry is empty
            if not char:
                return True

            # Get the current value in the entry
            entry_value = entry.get().strip()

            # Check if the number already exists in the same row
            for col in range(9):
                if col != current_col and self.entries[current_row][col].get().strip() == entry_value:
                    entry.delete(0, tk.END)
                    return False

            # Check if the number already exists in the same column
            for row in range(9):
                if row != current_row and self.entries[row][current_col].get().strip() == entry_value:
                    entry.delete(0, tk.END)
                    return False

            # Check if the number already exists in the same subgrid (3x3)
            start_row, start_col = (current_row // 3) * 3, (current_col // 3) * 3
            for i in range(start_row, start_row + 3):
                for j in range(start_col, start_col + 3):
                    if (i != current_row or j != current_col) and self.entries[i][j].get().strip() == entry_value:
                        entry.delete(0, tk.END)
                        return False

            # Highlight based on equality to sudoku_board
            if entry_value != str(sudoku_board[current_row][current_col]):
                self.highlight_entry(current_row, current_col, 'red')
            else:
                self.highlight_entry(current_row, current_col, 'green')

            if self.sudoku_domain:
                self.sudoku_domain.replace_all_cells(generate_domain_array(self.get_current_puzzle()))

            # Check if all cells are filled with numbers
            all_filled = all(entry.get().strip().isdigit() for row in self.entries for entry in row)
            if all_filled:
                self.readonly = True
                messagebox.showinfo("Congratulations!", "You solved the Sudoku puzzle!")

            # If no duplicate is found, return True
            return True

        self.entries = []
        for i in range(9):
            row = []
            for j in range(9):
                entry = tk.Entry(self.root, width=2, font=('Arial', 18), justify='center')
                entry.grid(row=i, column=j, padx=1, pady=1)
                entry.config(validate="key",
                             validatecommand=(entry.register(validate_input), "%S"))
                entry.bind('<KeyPress>', enforce_char_limit)
                entry.bind('<KeyRelease>', validate_row_col)
                row.append(entry)
            self.entries.append(row)

        self.generate_puzzle(puzzle)

    def generate_puzzle(self, puzzle):
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    self.entries[i][j].insert(0, puzzle[i][j])
                    self.entries[i][j].config(state='disabled')

    def highlight_entry(self, row, col, color):
        if color == 'green':
            bg_color = '#c8e6c9'  # Light green
        elif color == 'red':
            bg_color = '#ffcdd2'  # Light red
        else:
            bg_color = 'white'  # Default to white

        self.entries[row][col].config(bg=bg_color)

    def write_number(self, row, col, num):
        if 0 <= row < 9 and 0 <= col < 9:
            entry = self.entries[row][col]
            if entry['state'] == 'disabled':
                raise ValueError("Cannot write to a disabled entry")
            entry.delete(0, tk.END)  # Delete existing content
            entry.insert(0, num)

            # Highlight based on equality to sudoku_board
            if num != str(self.sol[row][col]):
                self.highlight_entry(row, col, 'red')
            else:
                self.highlight_entry(row, col, 'green')

        else:
            raise IndexError("Row and column indices out of bounds")

    def get_current_puzzle(self):
            current_puzzle = []
            for i in range(9):
                row_values = []
                for j in range(9):
                    entry_value = self.entries[i][j].get().strip()
                    if entry_value:
                        row_values.append(int(entry_value))
                    else:
                        row_values.append(0)
                current_puzzle.append(row_values)
            return current_puzzle


def test_caller():
    time.sleep(2)
    app.write_number(1, 1, 5)
    time.sleep(2)
    app.write_number(1, 1, 6)


if __name__ == "__main__":
    root = tk.Tk()
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
    app = SudokuGameGui(root, puzzle)

    # Create and start a new thread to execute commands
    thread = threading.Thread(target=test_caller)  # execute the algorithm and call update dynamically
    thread.start()

    root.mainloop()
