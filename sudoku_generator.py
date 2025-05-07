import random


class SudokuGenerator:
    def __init__(self):
        self.puzzle = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = None
        self.hidden_places = 51  # Default number of hidden places

    def is_valid(self, num, row, col):
        for i in range(9):
            if self.puzzle[row][i] == num or self.puzzle[i][col] == num:
                return False

        start_row, start_col = (row // 3) * 3, (col // 3) * 3
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if self.puzzle[i][j] == num:
                    return False

        return True

    def solve_sudoku(self):
        for row in range(9):
            for col in range(9):
                if self.puzzle[row][col] == 0:
                    nums = random.sample(range(1, 10), 9)
                    for num in nums:
                        if self.is_valid(num, row, col):
                            self.puzzle[row][col] = num
                            if self.solve_sudoku():
                                return True
                            self.puzzle[row][col] = 0
                    return False
        return True

    def generate_puzzle(self, deff):
        self.solve_sudoku()
        self.solution = [row[:] for row in self.puzzle]  # Make a deep copy of the solution
        # Randomly hide numbers in the puzzle
        hiddens = self.hidden_places
        if deff == "Easy":
            hiddens = 25
        elif deff == "Medium":
            hiddens = 35
        elif deff == "Hard":
            hiddens = 50

        for _ in range(hiddens):
            row, col = random.randint(0, 8), random.randint(0, 8)
            while self.puzzle[row][col] == 0:  # Ensure we don't hide an already hidden number
                row, col = random.randint(0, 8), random.randint(0, 8)
            self.puzzle[row][col] = 0
        return self.puzzle

    def get_solution(self):
        return self.solution


if __name__ == "__main__":
    generator = SudokuGenerator()
    puzzle = generator.generate_puzzle()
    for row in puzzle:
        print(row)
    print()
    print("Generated Sudoku:", generator.get_solution())