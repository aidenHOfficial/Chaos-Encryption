from GOL import GameOfLife
from RGOL import ReverseGameOfLife

alive_cells = set([(1, 1), (2, 1), (1, 2), (2, 2), (10, 10)])

print(f"Starting alive cells: {alive_cells}")

RGOL = ReverseGameOfLife(100, 100, alive_cells)

PAC = RGOL.previous_game_iteration()

print(f"Previous alive cells: {PAC}")

# GOL = GameOfLife(10, 10, alive_cells)

# NAC = GOL.get_next_alive_cells()
# NAC = GOL.get_next_alive_cells()

# print(f"Original alive cells: {alive_cells}")