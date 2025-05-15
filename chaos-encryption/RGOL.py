import json
import queue
import logging

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

    with open("dead_predecessors.json", "r") as f:
      self.dead_predecessors = set(json.load(f))

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
      s_cell = (((i % size) - radius), (radius - (i // size)))
      result = (s_cell[0] + cell[0], s_cell[1] + cell[1])
      if (result[0] > -1 and result[0] < self.width and result[1] > -1 and result[1] < self.length and result != cell):
        surrounding_cells.add(result)
    
    return surrounding_cells

  def are_compatible(self, config1, config2, bitmask1, bitmask2):
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
    previous_configs = self.get_previous_configs()

    if (previous_configs is None):
      return "Garden of Eden"
    
    previous_alive = set()
    for node, previous_config in previous_configs.items():
      previous_nodes = self.get_positions_from_binary(node, previous_config)
      previous_alive |= previous_nodes
      
    print(f"get_previous_alive_cells previous_alive: {previous_alive}")

    return previous_alive

  def get_previous_configs(self):
    constraints, domains, edges = self.get_arc_consistent_graph()

    with open("results.txt", "w") as file:
      file.write("Domains\n")
      for node, domain_set in domains.items():
        file.write(f"{node}: {domain_set}\n")

      file.write("\n\nConstraints\n")
      for node, constraint_set in constraints.items():
        file.write(f"{node}: \n")
        for constraint1, constraints2 in constraint_set.items():
          file.write(f" {constraint1}:")
          file.write(f"   {constraints2}\n")
        file.write(f"\n\n")

    solution = self.solve_constraints(constraints, domains, edges)

    print(f"get_previous_configs solution: {solution}")
    
    return solution

  def get_arc_consistent_graph(self):
    domains = {}
    edges = {}
    constraints = {}
    not_arc_consistent = set()
    agenda = queue.Queue()

    for c_cell in self.alive_cells:
      agenda.put(c_cell)

      neighboring_cells = self.get_surrounding_cells(c_cell, self.radius * 2)

      if c_cell not in edges:
        edges[c_cell] = set()

      for n_cell in neighboring_cells:
        if n_cell not in edges:
          edges[n_cell] = set()

        agenda.put(n_cell)

        edges[c_cell].add(n_cell)
        edges[n_cell].add(c_cell)

        if n_cell not in self.alive_cells:
          d_neighboring_cells = self.get_surrounding_cells(n_cell, self.radius * 2)
          d_neighboring_cells = d_neighboring_cells & neighboring_cells
          edges[n_cell] |= d_neighboring_cells

    while not agenda.empty():

      c_cell = agenda.get()

      if (c_cell not in domains):
        domains[c_cell] = self.alive_predecessors.copy()

      if (c_cell not in edges):
        edges[c_cell] = set()

      for n_cell in edges[c_cell]:
        if ((c_cell, n_cell) in constraints):
          continue
        elif ((c_cell, n_cell) not in constraints):
          constraints[(c_cell, n_cell)] = {}
          constraints[(n_cell, c_cell)] = {}
        
        if (n_cell not in domains):

          if (n_cell in self.alive_cells):
            domains[n_cell] = self.alive_predecessors.copy()
          else:
            domains[n_cell] = self.dead_predecessors.copy()

        bitmasks = self.get_bitmask_overlaps(
            c_cell,
            n_cell,
            self.get_surrounding_cells(c_cell, self.radius).union({c_cell}),
            self.get_surrounding_cells(n_cell, self.radius).union({n_cell})
        )
        used_neighbor_options = set()

        for domain_one_option in domains[c_cell].copy():
          for domain_two_option in domains[n_cell]:
            if (self.are_compatible(domain_one_option, domain_two_option, bitmasks[0], bitmasks[1])):
              
              if(domain_two_option not in used_neighbor_options):
                used_neighbor_options.add(domain_two_option)

              if (domain_one_option not in constraints[(c_cell, n_cell)]):
                constraints[(c_cell, n_cell)][domain_one_option] = set()
              if (domain_two_option not in constraints[(n_cell, c_cell)]):
                constraints[(n_cell, c_cell)][domain_two_option] = set()

              constraints[(c_cell, n_cell)][domain_one_option].add(domain_two_option)
              constraints[(n_cell, c_cell)][domain_two_option].add(domain_one_option)
          
          if (domain_one_option not in constraints[(c_cell, n_cell)]):
            domains[c_cell].remove(domain_one_option)
            not_arc_consistent.add((c_cell, n_cell))
        
        # Check if domain update needs to be added to not_arc_consisten t
        domains[n_cell] = used_neighbor_options
  
    for value in not_arc_consistent:
      agenda.put(value)

    while not agenda.empty():
      selected_constraint = agenda.get()

      to_remove = None
      if (selected_constraint[0] in self.alive_cells):
        to_remove = self.alive_predecessors.difference(domains[selected_constraint[0]])
      else:
        to_remove = self.dead_predecessors.difference(domains[selected_constraint[0]])

      constraints_to_update = {(selected_constraint[0], node2) for node2 in edges[selected_constraint[0]] if ((selected_constraint[0], node2) != selected_constraint)}

      for update_constraint in constraints_to_update:

        removed_constraint_options = set()
        for bad_option in to_remove:
          if bad_option in constraints[update_constraint]:
            for removed_constraint_option in constraints[update_constraint][bad_option]:
              removed_constraint_options.add(removed_constraint_option)
        
        for key in to_remove:
          constraints[update_constraint].pop(key, None)

        update_constraint_compliment = (update_constraint[1], update_constraint[0])

        for removed_constraint_option in removed_constraint_options:

          constraints[update_constraint_compliment][removed_constraint_option] -= to_remove

          if (len(constraints[update_constraint_compliment][removed_constraint_option]) == 0):
            if removed_constraint_option in domains[update_constraint_compliment[0]]:
              domains[update_constraint_compliment[0]].remove(removed_constraint_option)
            agenda.put(update_constraint_compliment)

    # simplified_constraints = {}

    # for constraint in constraints:
    #   ordered_constraint = tuple(sorted(constraint))

    #   if (ordered_constraint not in simplified_constraints):
    #     simplified_constraints[ordered_constraint] = constraints[ordered_constraint]

    return constraints, domains, edges

  def solve_constraints(self, constraints, domains, edges):

    def backtrack(selected_cells, node_index):

      if (node_index >= len(neighborly_nodes)):
        return selected_cells
      
      c_cell = neighborly_nodes[node_index]
      c_domain = {}

      if (c_cell in selected_cells):
        c_domain = selected_cells[c_cell]
      else:
        c_domain = domains[c_cell]
      
      for option in c_domain:
        selected_cells[c_cell] = option

        for n_cell in edges[c_cell]:

          if (n_cell in selected_cells and type(selected_cells[n_cell]) == set):
            selected_cells[n_cell] = selected_cells[n_cell] & constraints[(c_cell, n_cell)][option]

            # We know the selected option is within the restricted conditions of the other selections
            # since the domain selected is from the restricted set in selected_cells
            # elif (selected_cells[n_cell] not in constraints[(c_cell, n_cell)][option]):
            #   return None
        
          elif (n_cell not in selected_cells):
            selected_cells[n_cell] = constraints[(c_cell, n_cell)][option]

          if (type(selected_cells[n_cell]) == set and len(selected_cells[n_cell]) == 0 or selected_cells[n_cell] is None):
            return None
          
          result = backtrack(selected_cells, node_index + 1)
          if (result is not None):
            return result
          
      return None
    
    neighborly_nodes = list(edges.keys())

    solution = backtrack({}, 0)

    for cell in domains.keys():

      if cell not in solution:
        solution[cell] = next(iter(domains[cell]))
      elif cell in solution and type(solution[cell]) == set:
        solution[cell] = next(iter(solution[cell]))
      
    print(f"solve_constraints solution: {solution}")

    return solution

  def previous_game_iteration(self):
    self.alive_cells = self.get_previous_alive_cells()

    return self.alive_cells