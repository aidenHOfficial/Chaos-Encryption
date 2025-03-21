import json
from collections import defaultdict
import threading

import logging
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')



class ReverseGameOfLife:
  alive_cells = set()
  alive_predecessors = set()
  length = 0
  width = 0
  radius = 0

  def __init__(self, length, width, starting_cells):
    self.length = length
    self.width = width
    self.radius = 1
    self.alive_cells = starting_cells
    print(f"game started with starting_cells\n{self.alive_cells}")

    with open("alive_predecessors.json", "r") as f:
      self.alive_predecessors = set(json.load(f))

  def get_binary_from_position(self, position):
    # This method takes the centerpoint of the 3x3 config as an input
    # but works with the top left corner, so we transform the starting_x
    # and starting_y variables

    binary_number = 0

    starting_row = position[0] - 1
    starting_col = position[1] + 1

    for col in range(starting_col, starting_col - 3, -1):
      for row in range(starting_row, starting_row + 3):
        binary_number = (binary_number << 1) | ((row, col) in self.alive_cells)

    return bin(binary_number)

  def get_positions_from_binary(self, position, binary_string):
    length = ((2 * self.radius) + 1)
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
  
  def get_surrounding_cells(self, cell, radius):
    surrounding_cells = set()

    size = (radius * 2) + 1

    for i in range(size ** 2):
      # print(f"get_surrounding_cells iteration: {i}")
      s_cell = (((i % size) - radius), (radius - (i // size)))
      result = (s_cell[0] + cell[0], s_cell[1] + cell[1])
      if (result[0] > -1 and result[0] < self.width and result[1] > -1 and result[1] < self.length):
        surrounding_cells.add(result)
    
    return surrounding_cells

  def get_covers(self):
    covers = {}

    for cell in self.alive_cells:
      covers[cell] = self.get_surrounding_cells(cell, self.radius)
    
    # print(f"\nall possible covers: {covers}")

    return covers

  def are_compatible(self, config1, config2, bitmask1, bitmask2):
    config1 = int(config1, 2) if isinstance(config1, str) else config1
    config2 = int(config2, 2) if isinstance(config2, str) else config2
    bitmask1 = int(bitmask1, 2) if isinstance(bitmask1, str) else bitmask1
    bitmask2 = int(bitmask2, 2) if isinstance(bitmask2, str) else bitmask2

    masked_config1 = config1 & bitmask1
    masked_config2 = config2 & bitmask2

    # Normalize the bits for comparison
    bit_count1 = bin(bitmask1).count('1')
    bit_count2 = bin(bitmask2).count('1')

    normalized1 = masked_config1 >> (bitmask1.bit_length() - bit_count1)
    normalized2 = masked_config2 >> (bitmask2.bit_length() - bit_count2)

    # Compare normalized values
    return normalized1 == normalized2

  def get_bitmask_overlaps(self, centerPoint1, centerpoint2, cover1, cover2):

    size = ((2 * self.radius) + 1) ** 2

    mask1 = [0] * size
    mask2 = [0] * size

    for point in cover1:
      if (point in cover2):
        self.add_bit_from_positions(centerPoint1, point, mask1)
        self.add_bit_from_positions(centerpoint2, point, mask2)


    return (self.to_binary_number(mask1), self.to_binary_number(mask2))

  def add_bit_from_positions(self, centerPoint, newPoint, mask):
    relative_point = (newPoint[0] - centerPoint[0], newPoint[1] - centerPoint[1])
    overlap_index = (relative_point[0] + self.radius) + (self.radius - relative_point[1]) * ((2 * self.radius) + 1)
    mask[overlap_index] = 1
    return mask

  def to_binary_number(self, binary_string):
    return bin(int("".join(map(str, binary_string)), 2))

  def get_previous_alive_cells(self):
    harmonious_graph = self.find_harmonious_configuration_space()

  def find_harmonious_configuration_space(self):
    covers = self.get_covers()

    arc_consis_graph = self.get_arc_consistent_graph(covers)

    print(arc_consis_graph)

    # def backtrack(cell_config_graph, selected_tiles):

    #   if not cell_config_graph:
    #     return selected_tiles

    #   return backtrack(arc_consis_graph, {})



  def get_arc_consistent_graph(self, covers):
    edges = {}

    for cell in alive_cells:

      overlapping_cells = self.get_surrounding_cells(cell, self.radius * 2).intersection(alive_cells)

      for o_cell in overlapping_cells:

        if (o_cell == cell):
          continue

        edge = tuple(sorted((cell, o_cell)))

        bitmasks = self.get_bitmask_overlaps(cell, o_cell, covers[cell], covers[o_cell])

        if (edge not in edges):
          edges[edge] = {}

        if (cell not in edges): 
          cell_options = self.alive_predecessors
        else:
          cell_options = edges[edge].keys()

        if (o_cell not in edges[edge]):
          o_cell_options = self.alive_predecessors
        else:
          o_cell_options = edges[edge].keys()


        for option1 in cell_options:
          for option2 in o_cell_options:
            if (self.are_compatible(option1, option2, bitmasks[0], bitmasks[1])):
              if (option1 not in edges[edge]):
                edges[edge][option1] = set()
              edges[edge][option1].add(option2)
    
    return edges
 


cells = [(1, 1), (1, 2), (2, 2), (2, 1)]
alive_cells = set(cells)

RGOL = ReverseGameOfLife(10, 10, alive_cells)

RGOL.get_previous_alive_cells()