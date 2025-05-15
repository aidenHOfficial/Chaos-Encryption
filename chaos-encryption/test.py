import matplotlib.pyplot as plt 
import json
from collections import defaultdict

def get_surrounding_cells(width, length, cell, radius):
    surrounding_cells = set()

    size = (radius * 2) + 1

    for i in range(size ** 2):
      s_cell = (((i % size) - radius), (radius - (i // size)))
      result = (s_cell[0] + cell[0], s_cell[1] + cell[1])
      if (result[0] > -1 and result[0] < width and result[1] > -1 and result[1] < length):
        surrounding_cells.add(result)
    
    return surrounding_cells

def get_cell_scores(alive_cells, width, length, radius):

    score_dict = {}

    for cell in alive_cells:
        surrounding_cells = get_surrounding_cells(width, length, cell, radius)

        for s_cell in surrounding_cells:
            if(s_cell != cell):
                if (s_cell in score_dict):
                    score_dict[s_cell] += 1
                else:
                    score_dict[s_cell] = 1

    return score_dict

def get_next_alive_cells(alive_cells, width, length, radius):

    next_alive_cells = set()

    cell_scores = get_cell_scores(alive_cells, width, length, radius)
    
    for cell, score in cell_scores.items():
        if (score > 1 and score < 4):
            if (cell not in alive_cells and score == 3):
                next_alive_cells.add(cell)
            elif (cell in alive_cells):
                next_alive_cells.add(cell)

    return next_alive_cells

def get_binary_from_positions(position, alive_cells, radius):
    length = ((2 * radius) + 1)

    binary_string = ""

    starting_row = position[0] - 1
    starting_col = position[1] + 1

    for col in range(starting_col, starting_col - length, -1):
        for row in range(starting_row, starting_row + length):
            if ((row, col) in alive_cells):
                binary_string += "1"
            else:
                binary_string += "0"

    return binary_string

def get_positions_from_binary(position, binary_string, radius):
    length = ((2 * radius) + 1)
    binary_length = length ** 2

    binary_string = binary_string.replace("0b", "")
    if (len(binary_string) < binary_length):
        binary_string = binary_string.zfill(binary_length)

    cells = set()

    starting_x = position[0] - 1
    starting_y = position[1] + 1
    
    for i in range(len(binary_string)):
        if (binary_string[i] == "1"):
            cells.add((starting_x + (i % length), starting_y - (i // length)))

    return cells

def to_binary_number(binary_string):
    return bin(int("".join(map(str, binary_string)), 2))

def add_bit_from_positions(centerPoint, newPoint, mask, radius):
    relative_point = (newPoint[0] - centerPoint[0], newPoint[1] - centerPoint[1])
    overlap_index = (relative_point[0] + radius) + (radius - relative_point[1]) * ((2 * radius) + 1)
    mask[overlap_index] = 1
    return mask

def get_bitmask_overlaps(centerPoint1, centerpoint2, cover1, cover2, radius):
    size = ((2 * radius) + 1) ** 2

    mask1 = [0] * size
    mask2 = [0] * size

    for point in cover1:
        if (point in cover2):
            add_bit_from_positions(centerPoint1, point, mask1, radius)
            add_bit_from_positions(centerpoint2, point, mask2, radius)


    return (to_binary_number(mask1), to_binary_number(mask2))

def are_compatible(config1, config2, bitmask1, bitmask2):
    config1 = int(config1, 2) if isinstance(config1, str) else config1
    config2 = int(config2, 2) if isinstance(config2, str) else config2

    bitmask1 = int(bitmask1, 2) if isinstance(bitmask1, str) else bitmask1
    bitmask2 = int(bitmask2, 2) if isinstance(bitmask2, str) else bitmask2

    masked_config1 = config1 & bitmask1
    masked_config2 = config2 & bitmask2

    def msb_pos(n):
        if n != 0:
            return n.bit_length() - 1
        return -1

    shift1 = msb_pos(bitmask1)
    shift2 = msb_pos(bitmask2)

    if shift1 > shift2:
        masked_config2 <<= (shift1 - shift2)
    elif shift2 > shift1:
        masked_config1 <<= (shift2 - shift1)

    return masked_config1 == masked_config2

# config1 = "0b111000000"
# config2 = "0b000000000"
# bitmask1 = "0b111"
# bitmask2 = "111000000"

# print(are_compatible(config1, config2, bitmask1, bitmask2))

center_config = "0b10000"
center_bitmask = "0b000010000"

print(get_binary_from_positions((1, 1), [(1, 1)], 1))
living_predecessor = []
dead_predecessor = []

for i in range(2**9):
    config = bin(i)

    starting_points = get_positions_from_binary((1, 1), config, 1)

    next_alive = get_next_alive_cells(starting_points, 5, 5, 1)
    
    binary_next_alive = get_binary_from_positions((1, 1), next_alive, 1)

    # print(binary_next_alive)
    if (config == "0b11011000"):
        print(f"starting_config: {config} starting points: {starting_points} next_alive: {next_alive} binary_next_alive: {binary_next_alive}")

    if (are_compatible(binary_next_alive, center_config, center_bitmask, center_bitmask)):
        living_predecessor.append(to_binary_number(config))
    else:
        dead_predecessor.append(to_binary_number(config))

with open("alive_predecessors.json", "w") as f:
    json.dump(living_predecessor, f)

with open("dead_predecessors.json", "w") as f:
    json.dump(dead_predecessor, f)
