class GameOfLife:
    alive_cells = set()
    length = 0
    width = 0

    def __init__(self, length, width, starting_cells):
        self.radius = 1
        self.length = length
        self.width = width
        self.alive_cells = starting_cells
        print(f"game started with starting_cells\n{self.alive_cells}")

    def set_game_moore(self):
        self.surrounding_array = [(0, 1), (-1, 0), (1, 0), (0, -1)]

    def set_game_van_neumann(self):
        self.surrounding_array = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]

    def get_surrounding_cells(self, cell, radius):
        surrounding_cells = set()

        size = (radius * 2) + 1

        for i in range(size ** 2):
            s_cell = (((i % size) - radius), (radius - (i // size)))
            result = (s_cell[0] + cell[0], s_cell[1] + cell[1])
            if (result[0] > -1 and result[0] < self.width and result[1] > -1 and result[1] < self.length):
                surrounding_cells.add(result)
        
        return surrounding_cells

    def get_cell_scores(self):

        score_dict = {}

        for cell in self.alive_cells:

            surrounding_cells = self.get_surrounding_cells(cell, self.radius)

            for cell in surrounding_cells:
                if (cell in score_dict):
                    score_dict[cell] += 1
                else:
                    score_dict[cell] = 1

        return score_dict

    def get_next_alive_cells(self):

        next_alive_cells = set()

        cell_scores = self.get_cell_scores()

        for cell, score in cell_scores.items():
            if (score > 1 and score < 4):
                if (cell not in self.alive_cells and score == 3):
                    next_alive_cells.add(cell)
                elif (cell in self.alive_cells):
                    next_alive_cells.add(cell)


        self.alive_cells = next_alive_cells

        return next_alive_cells
    
    def next_game_iteration(self):
        self.alive_cells = self.get_next_alive_cells()

        return self.alive_cells