import tkinter as tk
from tkinter import ttk
import time
import threading
from helper import generate_domain_array

def get_color(number):
    """Generate a color gradient based on domain size (smaller domain = darker color)"""
    if number == 1:
        return "#FF6B6B"  # Bright red for solved cells
    
    # Gradient from blue-green (large domain) to purple (small domain)
    normalized_number = (9 - number) / 8.0  # Smaller domains get higher values
    
    # Color palette: Blue-green gradient to purple
    if normalized_number < 0.33:  # Larger domains (blue-green)
        r = max(0, min(255, int(41 + 90 * (normalized_number * 3))))
        g = max(0, min(255, int(128 + 41 * (normalized_number * 3))))
        b = max(0, min(255, int(185 + 15 * (normalized_number * 3))))
    elif normalized_number < 0.66:  # Medium domains (teal to light purple)
        factor = (normalized_number - 0.33) * 3
        r = max(0, min(255, int(71 + 84 * factor)))
        g = max(0, min(255, int(142 - 42 * factor)))
        b = max(0, min(255, int(190 - 30 * factor)))
    else:  # Smaller domains (purple variants)
        factor = (normalized_number - 0.66) * 3
        r = max(0, min(255, int(155 + 55 * factor)))
        g = max(0, min(255, int(100 - 30 * factor)))
        b = max(0, min(255, int(160 + 35 * factor)))
    
    # Ensure proper formatting of hex colors with leading zeros
    return f'#{r:02x}{g:02x}{b:02x}'


class SudokuDomain:
    def __init__(self, root, cell_data):
        self.root = root
        self.cells = []
        
        # Calculate initial possibility count
        self.total_possibilities = self._count_possibilities(cell_data)
        
        # Create main container with gradient background
        self.container = tk.Frame(root, bg="#F0F0F0")
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create header with gradient background
        self.header = tk.Frame(self.container, bg="#4B6584", height=60)
        self.header.pack(fill=tk.X, padx=0, pady=0)
        
        # Title with drop shadow effect
        self.title_frame = tk.Frame(self.header, bg="#4B6584")
        self.title_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.title_shadow = tk.Label(self.title_frame, text="Domain Visualization", 
                                   font=('Arial', 18, 'bold'), fg="#2C3A47", bg="#4B6584")
        self.title_shadow.grid(row=0, column=0, padx=2, pady=2)
        
        self.title_label = tk.Label(self.title_frame, text="Domain Visualization", 
                                  font=('Arial', 18, 'bold'), fg="#F5F6FA", bg="#4B6584")
        self.title_label.grid(row=0, column=0)
        
        # Add a frame to contain the counter and description
        self.info_frame = tk.Frame(self.container, bg="#F0F0F0", padx=10, pady=10)
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add statistics section with counter
        self.stats_frame = tk.LabelFrame(self.info_frame, text="Statistics", 
                                        font=('Arial', 10, 'bold'), bg="#F0F0F0",
                                        fg="#2C3A47", padx=15, pady=10)
        self.stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.possibilities_label = tk.Label(self.stats_frame, 
                                         text=f"Remaining possibilities: {self.total_possibilities}",
                                         font=('Arial', 11), bg="#F0F0F0", fg="#2C3A47")
        self.possibilities_label.pack(anchor='w')
        
        self.cells_with_multiple_label = tk.Label(self.stats_frame, 
                                               text=f"Cells with multiple options: {self._count_unfilled_cells(cell_data)}",
                                               font=('Arial', 11), bg="#F0F0F0", fg="#2C3A47")
        self.cells_with_multiple_label.pack(anchor='w', pady=(5,0))
        
        # Progress bar for solving progress
        self.progress_label = tk.Label(self.stats_frame, text="Solving progress:", 
                                     font=('Arial', 11), bg="#F0F0F0", fg="#2C3A47")
        self.progress_label.pack(anchor='w', pady=(10,2))
        
        self.progress_style = ttk.Style()
        self.progress_style.theme_use('default')
        self.progress_style.configure("Custom.Horizontal.TProgressbar", 
                                    background='#5758BB', troughcolor='#F0F0F0',
                                    borderwidth=0, thickness=20)
        
        # Calculate initial progress
        initial_progress = self._calculate_progress(cell_data)
        
        self.progress_bar = ttk.Progressbar(self.stats_frame, style="Custom.Horizontal.TProgressbar",
                                          orient="horizontal", length=200, mode="determinate")
        self.progress_bar["value"] = initial_progress
        self.progress_bar.pack(anchor='w', pady=(0, 10))
        
        # Description of the visualization
        self.legend_frame = tk.LabelFrame(self.info_frame, text="Legend", 
                                        font=('Arial', 10, 'bold'), bg="#F0F0F0",
                                        fg="#2C3A47", padx=15, pady=10)
        self.legend_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add color legend
        self.create_color_legend(self.legend_frame)
        
        # Create a frame for the grid with border
        self.grid_container = tk.Frame(self.container, bg="#E0E0E0", padx=10, pady=10,
                                    highlightbackground="#3C4453", highlightthickness=2)
        self.grid_container.pack(padx=15, pady=(5, 15))
        
        self.grid_frame = tk.Frame(self.grid_container, bg="#E0E0E0")
        self.grid_frame.pack(padx=5, pady=5)
        
        # Create the actual grid
        self.create_grid(cell_data)

    def create_color_legend(self, parent):
        """Create a color legend showing what different colors mean"""
        # Create a frame for the legend items
        legend_items = [
            ("1 possibility", get_color(1)),
            ("2-3 possibilities", get_color(3)),
            ("4-6 possibilities", get_color(5)),
            ("7-9 possibilities", get_color(8)),
            ("Fixed cells", "#DDDDDD")
        ]
        
        for idx, (text, color) in enumerate(legend_items):
            frame = tk.Frame(parent, bg="#F0F0F0")
            frame.pack(anchor='w', pady=(0, 5))
            
            # Color sample
            sample = tk.Frame(frame, width=20, height=20, bg=color, 
                             highlightbackground="#555555", highlightthickness=1)
            sample.pack(side=tk.LEFT, padx=(0, 10))
            sample.pack_propagate(False)
            
            # Text description
            label = tk.Label(frame, text=text, font=('Arial', 9), bg="#F0F0F0", fg="#2C3A47")
            label.pack(side=tk.LEFT)

    def _count_possibilities(self, cell_data):
        """Count total number of domain possibilities in the grid"""
        count = 0
        for row in cell_data:
            for cell in row:
                if cell["color"] == "white":
                    count += len(cell["domain"])
                else:
                    count += 1  # Fixed cells have one possibility
        return count
    
    def _count_unfilled_cells(self, cell_data):
        """Count cells that have multiple possibilities"""
        count = 0
        for row in cell_data:
            for cell in row:
                if cell["color"] == "white" and len(cell["domain"]) > 1:
                    count += 1
        return count
    
    def _calculate_progress(self, cell_data):
        """Calculate solving progress as a percentage"""
        total_cells = 81
        filled_cells = 0
        
        for row in cell_data:
            for cell in row:
                if cell["color"] == "gray" or len(cell["domain"]) == 1:
                    filled_cells += 1
        
        return (filled_cells / total_cells) * 100

    def create_grid(self, cell_data):
        # Create the outer 3x3 grid segments
        for segment_row in range(3):
            for segment_col in range(3):
                segment_frame = tk.Frame(self.grid_frame, bg="#333333", padx=2, pady=2)
                segment_frame.grid(row=segment_row, column=segment_col, padx=3, pady=3)
                
                # Create the inner 3x3 cells within each segment
                for i in range(3):
                    for j in range(3):
                        row = segment_row * 3 + i
                        col = segment_col * 3 + j
                        
                        cell_value = cell_data[row][col]["value"]
                        cell_color = "#DDDDDD"  # Default gray for fixed cells
                        
                        if cell_data[row][col]["color"] == "white":
                            cell_value = cell_data[row][col]["domain"]
                            cell_color = get_color(len(cell_value))
                        
                        # Create a frame for each cell
                        cell = tk.Frame(segment_frame, width=65, height=65, 
                                       bg=cell_color, highlightbackground="#666666",
                                       highlightthickness=1)
                        cell.grid(row=i, column=j, padx=1, pady=1)
                        cell.grid_propagate(False)  # Maintain fixed size
                        
                        # Center the content in the cell
                        cell.grid_columnconfigure(0, weight=1)
                        cell.grid_rowconfigure(0, weight=1)
                        
                        # Create a label for the domain values
                        label = tk.Label(cell, bg=cell_color, font=('Arial', 9), justify='center')
                        label.grid(sticky='nsew')
                        
                        if len(cell_value) == 1 and cell_data[row][col]["color"] == "gray":
                            # For fixed cells, make the font larger and bold
                            label.config(font=('Arial', 14, 'bold'), fg="#2C3E50")
                        elif len(cell_value) == 1:
                            # For solved cells, make the font larger
                            label.config(font=('Arial', 14), fg="#2C3E50")
                        
                        # Format the domain values in a clean way
                        display_text = self.format_domain_text(cell_value)
                        label.config(text=display_text)
                        
                        self.cells.append({
                            "row": row, "col": col,
                            "frame": cell, "label": label, 
                            "value": cell_value, "fixed": cell_data[row][col]["color"] == "gray"
                        })

    def format_domain_text(self, domain_values):
        """Format domain values in a clean 3x3 grid for display"""
        if len(domain_values) == 1:
            # For solved cells, display the value prominently
            return str(domain_values[0])
        
        # Create a 3x3 grid of possible values
        grid = [" " for _ in range(9)]
        for val in domain_values:
            grid[val-1] = str(val)
        
        return f"{grid[0]} {grid[1]} {grid[2]}\n{grid[3]} {grid[4]} {grid[5]}\n{grid[6]} {grid[7]} {grid[8]}"

    def update_cell(self, row, col, new_value):
        """Update a single cell with new domain values"""
        # Find the cell at the specified position
        old_domain_size = 0
        
        for cell in self.cells:
            if cell["row"] == row and cell["col"] == col:
                old_domain_size = len(cell["value"])
                cell_color = "#DDDDDD" if cell["fixed"] else get_color(len(new_value))
                
                # Add a brief highlight effect
                cell["frame"].config(bg="#FFCC99")
                self.root.update_idletasks()
                time.sleep(0.05)
                
                # Update the cell's visual appearance
                cell["frame"].config(bg=cell_color)
                cell["label"].config(bg=cell_color)
                
                # Update font based on domain size
                if len(new_value) == 1:
                    cell["label"].config(font=('Arial', 14), fg="#2C3E50")
                else:
                    cell["label"].config(font=('Arial', 9), fg="black")
                
                # Update the text with formatted domain values
                display_text = self.format_domain_text(new_value)
                cell["label"].config(text=display_text)
                
                # Update cell data
                cell["value"] = new_value
                
                # Update possibility counter (subtract removed possibilities)
                self.total_possibilities -= (old_domain_size - len(new_value))
                self.update_statistics()
                
                # Force update to show changes immediately
                self.root.update_idletasks()
                break

    def assign_digit(self, row, col, digit):
        """Assign a digit to a cell and update related cells with animation"""
        # Find the target cell
        target_cell = None
        old_domain_size = 0
        
        for cell in self.cells:
            if cell["row"] == row and cell["col"] == col:
                target_cell = cell
                old_domain_size = len(cell["value"])
                break
        
        if not target_cell:
            return
            
        # Highlight the cell being assigned with a pulse animation
        self._pulse_highlight(target_cell["frame"], "#FF9999", "#FFDDDD", 3)
        
        # Set the value
        target_cell["value"] = [digit]
        display_text = self.format_domain_text([digit])
        target_cell["label"].config(text=display_text, font=('Arial', 14), fg="#2C3E50")
        
        # Update the cell color to indicate solved state
        cell_color = get_color(1)
        target_cell["frame"].config(bg=cell_color)
        target_cell["label"].config(bg=cell_color)
        
        # Update possibility counter
        self.total_possibilities -= (old_domain_size - 1)
        self.update_statistics()
        
        # Update related cells in the same row, column and box
        self._update_related_cells(row, col, digit)
    
    def _pulse_highlight(self, widget, color1, color2, repeats=3):
        """Create a pulsing highlight effect"""
        original_bg = widget.cget("bg")
        
        for _ in range(repeats):
            widget.config(bg=color1)
            self.root.update_idletasks()
            time.sleep(0.1)
            widget.config(bg=color2)
            self.root.update_idletasks()
            time.sleep(0.1)
        
        widget.config(bg=original_bg)
        
    def update_statistics(self):
        """Update the statistics display"""
        # Count unfilled cells
        unfilled_cells = 0
        for cell in self.cells:
            if not cell["fixed"] and len(cell["value"]) > 1:
                unfilled_cells += 1
        
        # Update labels
        self.possibilities_label.config(text=f"Remaining possibilities: {self.total_possibilities}")
        self.cells_with_multiple_label.config(text=f"Cells with multiple options: {unfilled_cells}")
        
        # Update progress bar
        filled_cells = 81 - unfilled_cells
        progress = (filled_cells / 81) * 100
        self.progress_bar["value"] = progress
        
        # Update colors based on progress
        if progress > 75:
            self.progress_style.configure("Custom.Horizontal.TProgressbar", background='#26de81')
        elif progress > 50:
            self.progress_style.configure("Custom.Horizontal.TProgressbar", background='#fed330')
        else:
            self.progress_style.configure("Custom.Horizontal.TProgressbar", background='#5758BB')
        
    def _update_related_cells(self, row, col, digit):
        """Update all cells affected by placing a digit at (row, col)"""
        # Get all cells in the same row, column, and box
        affected_cells = []
        
        for cell in self.cells:
            r, c = cell["row"], cell["col"]
            same_row = r == row and c != col
            same_col = c == col and r != row
            same_box = (r // 3 == row // 3 and c // 3 == col // 3 and 
                       not (r == row and c == col))
            
            if same_row or same_col or same_box:
                affected_cells.append(cell)
        
        # Remove the digit from affected cells
        domains_changed = False
        
        for cell in affected_cells:
            if digit in cell["value"] and len(cell["value"]) > 1:
                # Highlight cell briefly
                cell["frame"].config(bg="#FFCC99")
                self.root.update_idletasks()
                time.sleep(0.03)
                
                # Update domain
                cell["value"].remove(digit)
                display_text = self.format_domain_text(cell["value"])
                cell["label"].config(text=display_text)
                
                # Update color
                cell_color = get_color(len(cell["value"]))
                cell["frame"].config(bg=cell_color)
                cell["label"].config(bg=cell_color)
                
                # Update font if this cell now has only one possibility
                if len(cell["value"]) == 1:
                    cell["label"].config(font=('Arial', 14), fg="#2C3E50")
                
                self.total_possibilities -= 1
                domains_changed = True
                
                self.root.update_idletasks()
        
        if domains_changed:
            self.update_statistics()

    def replace_all_cells(self, new_cell_data):
        """Replace all cell data with new values"""
        # Calculate new total possibilities
        new_possibilities = self._count_possibilities(new_cell_data)
        possibility_diff = self.total_possibilities - new_possibilities
        self.total_possibilities = new_possibilities
        
        # Create a flattened dictionary for easier lookup
        cell_dict = {}
        for cell in self.cells:
            key = (cell["row"], cell["col"])
            cell_dict[key] = cell
        
        # Update each cell
        for i in range(9):
            for j in range(9):
                new_value = new_cell_data[i][j]["value"]
                if new_cell_data[i][j]["color"] == "white":
                    new_value = new_cell_data[i][j]["domain"]
                
                cell = cell_dict.get((i, j))
                if cell:
                    # Update cell color and value
                    is_fixed = new_cell_data[i][j]['color'] == "gray"
                    cell_color = "#DDDDDD" if is_fixed else get_color(len(new_value))
                    
                    cell["frame"].config(bg=cell_color)
                    cell["label"].config(bg=cell_color)
                    
                    # Update font based on domain size
                    if len(new_value) == 1:
                        if is_fixed:
                            cell["label"].config(font=('Arial', 14, 'bold'), fg="#2C3E50")
                        else:
                            cell["label"].config(font=('Arial', 14), fg="#2C3E50")
                    else:
                        cell["label"].config(font=('Arial', 9), fg="black")
                    
                    display_text = self.format_domain_text(new_value)
                    cell["label"].config(text=display_text)
                    
                    cell["value"] = new_value
                    cell["fixed"] = is_fixed
        
        # Update statistics
        self.update_statistics()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sudoku Domain Visualization")
    root.geometry("700x800")  # Larger window size
    root.configure(bg="#F0F0F0")  # Light gray background
    
    # Set application icon (you'll need to add the icon file)
    try:
        root.iconbitmap("sudoku_icon.ico")
    except:
        pass  # Icon not found, ignore
        
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

    cell_data = generate_domain_array(puzzle)
    sudoku_grid = SudokuDomain(root, cell_data)
    
    # Demo: Update a cell after a delay (simulating solving)
    def demo_update():
        time.sleep(1)
        sudoku_grid.assign_digit(0, 2, 4)
        time.sleep(1)
        sudoku_grid.assign_digit(0, 3, 6)
    
    # Run the demo in a separate thread
    # thread = threading.Thread(target=demo_update)
    # thread.daemon = True
    # thread.start()

    root.mainloop()
