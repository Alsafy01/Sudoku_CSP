import tkinter as tk
import copy
import time

from helper import generate_domain_array
from sudoku_solver import run
from sudoku_board import SudokuGameGui
from sudoku_generator import SudokuGenerator
from sudoku_domain import SudokuDomain


# Helpers
def get_puzzle_mode():
    mode = selected_mode.get()
    deff = selected_difficulty.get()
    if mode == "Random":
        # Generate a random sudoku
        generator = SudokuGenerator()
        puzzle = generator.generate_puzzle(deff)
        print("Generated Sudoku:",generator.get_solution())
    elif mode == "Input":
        # Construct the puzzle from the values entered in the main window
        puzzle = []
        for i in range(9):
            row_values = []
            for j in range(9):
                entry_value = entries[i][j].get().strip()
                if entry_value:
                    row_values.append(int(entry_value))
                else:
                    row_values.append(0)
            puzzle.append(row_values)
    else:
        # Raise an error for unknown mode
        raise ValueError("Unknown mode selected")
    return puzzle


def get_selected_difficulty():
    return selected_difficulty.get()


def move_cursor(event, row, col):
    print("in")
    # Ensure that the new row and column are within the bounds of the puzzle
    if 0 <= row < 9 and 0 <= col < 9:
        # Set the focus to the entry widget at the new row and column
        entries[row][col].focus_set()


# Buttons
def user_button_click():
    sol = get_puzzle_mode()
    sudoku_board = copy.deepcopy(sol)
    root.destroy()  # Close the main window
    run(sol)

    # Create a new Tkinter window for SudokuGameGui
    new_root_game = tk.Tk()
    new_root_game.title("Sudoku Game")

    # Create a new Tkinter window for SudokuDomain
    new_root_domain = tk.Toplevel()
    new_root_domain.title("Sudoku Domains")

    # Initialize the SudokuDomain object
    cell_data = generate_domain_array(sudoku_board)
    sudoku_domain = SudokuDomain(new_root_domain, cell_data)
    # Create the SudokuGameGui object with the SudokuDomain
    app = SudokuGameGui(new_root_game, sudoku_board, sol, sudoku_domain)

    # Calculate the screen width and height
    screen_width = new_root_game.winfo_screenwidth()
    screen_height = new_root_game.winfo_screenheight()

    # Calculate the window width and height
    window_width = 500
    window_height = 700

    # Calculate the x and y positions for both windows
    x_game = (screen_width // 2) - (window_width // 2)
    y_game = (screen_height // 2) - (window_height // 2)

    x_domain = x_game + window_width + 10  # Add a gap of 10 pixels between windows
    y_domain = y_game

    # Set the geometry for both windows
    # new_root_game.geometry(f"{window_width}x{window_height}+{x_game}+{y_game}")
    new_root_domain.geometry(f"{window_width}x{window_height}+{x_domain}+{y_domain}")

    # Start the main event loop for both windows
    new_root_game.mainloop()
    new_root_domain.mainloop()


def AI_button_click():
    puzzle = get_puzzle_mode()
    sudoku_board = copy.deepcopy(puzzle)
    root.destroy()  # Close the main window
    run(puzzle)

    new_root = tk.Tk()
    new_root.title("Sudoku Game")
    app = SudokuGameGui(new_root, sudoku_board, puzzle, edit_block=True)

    # Define a recursive function to fill the cells with a delay
    def fill_cells(row, col):
        if row == 9:
            return  # Exit when all rows are filled
        if col == 9:
            fill_cells(row + 1, 0)  # Move to the next row
            return
        if sudoku_board[row][col] == 0:
            num = puzzle[row][col]
            # new_root.after(1000, app.write_number, row, col, num)  # Call write_number after 1 second
            time.sleep(0.3)
            app.write_number(row, col, num)
            new_root.update()  # Update the GUI to reflect changes
        fill_cells(row, col + 1)  # Move to the next column

    if puzzle:
        fill_cells(0, 0)  # Start filling cells from the first cell

    new_root.mainloop()


# Validations
def validate_input(char):
    if char.isdigit() and 1 <= int(char) <= 9:
        return True
    return False


def enforce_char_limit(event):
    entry = event.widget
    if len(entry.get()) > 0:
        entry.delete(0, tk.END)
    if event.char.isdigit() and 1 <= int(event.char) <= 9:
        entry.insert(0, event.char)
    return 'break'


def validate_row_col(event):
    entry = event.widget
    char = entry.get().strip()
    current_row, current_col = int(entry.grid_info()["row"]), int(entry.grid_info()["column"])

    # Get the current value in the entry
    entry_value = entry.get().strip()

    # Check if the number already exists in the same row
    for col in range(9):
        if col != current_col and entries[current_row][col].get().strip() == entry_value:
            # print_board()
            # show_error_message("Duplicate digit in the same row!")
            entry.delete(0, tk.END)
            return False

    # Check if the number already exists in the same column
    for row in range(9):
        if row != current_row and entries[row][current_col].get().strip() == entry_value:
            # print_board()
            # show_error_message("Duplicate digit in the same column!")
            entry.delete(0, tk.END)
            return False

    # Check if the number already exists in the same subgrid (3x3)
    start_row, start_col = (current_row // 3) * 3, (current_col // 3) * 3
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if (i != current_row or j != current_col) and entries[i][j].get().strip() == entry_value:
                # print_board()
                # show_error_message("Duplicate digit in the same subgrid!")
                entry.delete(0, tk.END)
                return False

    # If no duplicate is found, return True
    return True


# Create the main window
root = tk.Tk()
root.title("Sudoku Game")

# Define the 9x9 grid layout
grid_frame = tk.Frame(root)
grid_frame.grid(row=0, column=0)

# Create a 9x9 grid of Entry widgets to represent the Sudoku puzzle
entries = []
for i in range(9):
    row = []
    for j in range(9):
        entry = tk.Entry(grid_frame, width=2, font=('Arial', 18), justify='center')
        entry.grid(row=i, column=j, padx=1, pady=1)
        # Add constraints to only allow single digits from 1 to 9
        entry.config(validate="key",
                     validatecommand=(entry.register(validate_input), "%S"))
        # Bind events for enforcing single character limit and row-column validation
        entry.bind('<KeyPress>', enforce_char_limit)
        entry.bind('<KeyRelease>', validate_row_col)
        # Bind arrow key events to move_cursor function
        entry.bind('<Up>', lambda event, i=i, j=j: move_cursor(event, i-1, j))
        entry.bind('<Down>', lambda event, i=i, j=j: move_cursor(event, i+1, j))
        entry.bind('<Left>', lambda event, i=i, j=j: move_cursor(event, i, j-1))
        entry.bind('<Right>', lambda event, i=i, j=j: move_cursor(event, i, j+1))
        row.append(entry)
    entries.append(row)


# Create the "Solve" button
solve_button = tk.Button(root, text="Solve", bg="blue", fg="white", font=('Arial', 12), command=AI_button_click)
solve_button.grid(row=1, column=0, pady=10)

# Create the "Let Me Try" button
try_button = tk.Button(root, text="Let Me Try", bg="green", fg="white", font=('Arial', 12), command=user_button_click)
try_button.grid(row=2, column=0, pady=10)

# Create radio buttons
selected_mode = tk.StringVar()

# By default, "Random" mode is selected
selected_mode.set("Random")

random_radio = tk.Radiobutton(root, text="Random", variable=selected_mode, value="Random")
random_radio.grid(row=3, column=0, pady=5)

input_radio = tk.Radiobutton(root, text="Input", variable=selected_mode, value="Input")
input_radio.grid(row=4, column=0, pady=5)

# Create radio buttons for difficulty levels
selected_difficulty = tk.StringVar()

# By default, "Easy" difficulty is selected
selected_difficulty.set("Easy")

easy_radio = tk.Radiobutton(root, text="Easy", variable=selected_difficulty, value="Easy", font=('Arial', 12))
easy_radio.grid(row=5, column=0, pady=5)

medium_radio = tk.Radiobutton(root, text="Medium", variable=selected_difficulty, value="Medium", font=('Arial', 12))
medium_radio.grid(row=6, column=0, pady=5)

hard_radio = tk.Radiobutton(root, text="Hard", variable=selected_difficulty, value="Hard", font=('Arial', 12))
hard_radio.grid(row=7, column=0, pady=5)


root.mainloop()
