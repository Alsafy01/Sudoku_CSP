import threading
import time
import tkinter as tk
from tkinter import messagebox
from queue import Queue

from helper import generate_domain_array
from sudoku_domain import SudokuDomain


def domain_caller(sudoku_board, sudoku_domain, result_queue):
    time.sleep(1)  # Simulating some computation time
    solver = SudokuSolver(sudoku_board, sudoku_domain)
    start = time.time()
    if solver.solve():
        end = time.time()
        print("Solution found:")
        for row in solver.board:
            print(row)
        print("execution time :", (end-start) * 10**3, "ms")
        result = solver.board
        result_queue.put(result)
    else:
        print("No solution exists.")
        messagebox.showinfo("Unsolvable!", "Your Sudoku is an unsolvable puzzle!")
        result_queue.put(None)


class SudokuSolver:
    def __init__(self, board, sudoku_domain):
        self.board = board
        self.sudoku_domain = sudoku_domain

    def solve(self):
        # Find the first empty cell in the board
        empty_cell = self.find_empty_cell()

        # If there are no empty cells, the puzzle is solved
        if not empty_cell:
            return True

        row, col = empty_cell

        # Try filling in a digit from 1 to 9
        for num in range(1, 10):
            if self.is_valid_move(row, col, num):
                # If the move is valid, set the cell to the chosen number
                self.board[row][col] = num
                # Replace all cells in sudoku_domain after assumption

                self.sudoku_domain.replace_all_cells(generate_domain_array(self.board))

                # Recursively try to solve the rest of the puzzle
                if self.solve():
                    return True

                # If the puzzle cannot be solved with this choice, backtrack
                self.board[row][col] = 0

        # If no valid number can be placed, backtrack to the previous cell
        return False

    def find_empty_cell(self):
        # Find the first empty cell in the board
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    return (row, col)
        return None

    def is_valid_move(self, row, col, num):
        # Check if the chosen number is valid for the given cell
        return (
                not self.used_in_row(row, num) and
                not self.used_in_col(col, num) and
                not self.used_in_box(row - row % 3, col - col % 3, num)
        )

    def used_in_row(self, row, num):
        # Check if the number is used in the same row
        return num in self.board[row]

    def used_in_col(self, col, num):
        # Check if the number is used in the same column
        return num in [self.board[i][col] for i in range(9)]

    def used_in_box(self, box_start_row, box_start_col, num):
        # Check if the number is used in the 3x3 box
        for i in range(3):
            for j in range(3):
                if self.board[i + box_start_row][j + box_start_col] == num:
                    return True
        return False


def run(sudoku_board):
    root = tk.Tk()
    root.title("Sudoku Solver Test")
    cell_data = generate_domain_array(sudoku_board)
    sudoku_domain = SudokuDomain(root, cell_data)

    result_queue = Queue()

    thread = threading.Thread(target=domain_caller, args=(sudoku_board, sudoku_domain, result_queue))
    thread.start()

    root.mainloop()

    # Wait for the thread to finish
    thread.join()

    # Get the returned value from the queue
    returned_value = result_queue.get()

    return returned_value


if __name__ == "__main__":
    # Example Sudoku board
    sudoku_board = [
    [0, 0, 3, 0, 2, 0, 6, 0, 0],
    [9, 0, 0, 3, 0, 5, 0, 0, 1],
    [0, 0, 1, 8, 0, 6, 4, 0, 0],
    [0, 0, 8, 1, 0, 2, 9, 0, 0],
    [7, 0, 0, 0, 0, 0, 0, 0, 8],
    [0, 0, 6, 7, 0, 8, 2, 0, 0],
    [0, 0, 2, 6, 0, 9, 5, 0, 0],
    [8, 0, 0, 2, 0, 3, 0, 0, 9],
    [0, 0, 5, 0, 1, 0, 3, 0, 0]
]
    run(sudoku_board)