def generate_domain_array(puzzle):
    domain_array = []
    for i in range(9):
        row = []
        for j in range(9):
            if puzzle[i][j] == 0:  # Check if the cell is empty
                # Determine the domain for an empty cell
                domain = set(range(1, 10))  # All possible values from 1 to 9
                # Check the row and column to remove used values
                for k in range(9):
                    if puzzle[i][k] != 0:  # Check row
                        domain.discard(puzzle[i][k])
                    if puzzle[k][j] != 0:  # Check column
                        domain.discard(puzzle[k][j])
                # Check the segment to remove used values
                segment_row = i // 3
                segment_col = j // 3
                for m in range(segment_row * 3, segment_row * 3 + 3):
                    for n in range(segment_col * 3, segment_col * 3 + 3):
                        if puzzle[m][n] != 0:  # Check segment
                            domain.discard(puzzle[m][n])
                row.append({"value": [0], "color": "white", "domain": list(domain)})
            else:
                row.append({"value": [puzzle[i][j]], "color": "gray", "domain": []})  # Gray color for given values
        domain_array.append(row)
    return domain_array
