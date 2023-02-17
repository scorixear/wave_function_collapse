from tile import Tile
import random
class Cell:
    def __init__(self, possible: list, x: int, y: int) -> None:
        self.possible = possible
        self.collapsed = False
        self.x = x
        self.y = y
    def __str__(self) -> str:
        return f"{str(self.possible)}: {self.collapsed}"
    def __repr__(self) -> str:
        return self.__str__()
    def _reduce_single_side(self, grid: list[list['Cell']], tiles: dict[str, Tile], new_x: int, new_y: int, own_side: int, other_side: int):
        possible_cells = []
        left_cells = grid[new_y][new_x].possible
        left_sockets = list(map(lambda cell: tiles[cell].sides[other_side], left_cells))
        for self_tile in self.possible:
            if tiles[self_tile].sides[own_side][::-1] in left_sockets:
                possible_cells.append(self_tile)
        return possible_cells
    def reduce(self, grid: list[list['Cell']], tiles: dict[str, Tile]) -> tuple[set, list[tuple[int, int]]]:
        possible_cells = self.possible
        affected = []
        if self.x > 0:
            affected.append((self.x-1, self.y))
            possible_cells = list(filter(lambda cell: cell in possible_cells, self._reduce_single_side(grid, tiles, self.x-1, self.y, 3, 1)))
        if self.x < len(grid[0])-1:
            affected.append((self.x+1, self.y))
            possible_cells = list(filter(lambda cell: cell in possible_cells, self._reduce_single_side(grid, tiles, self.x+1, self.y, 1, 3)))
        if self.y > 0:
            affected.append((self.x, self.y-1))
            possible_cells = list(filter(lambda cell: cell in possible_cells, self._reduce_single_side(grid, tiles, self.x, self.y-1, 0, 2)))
        if self.y < len(grid)-1:
            affected.append((self.x, self.y+1))
            possible_cells = list(filter(lambda cell: cell in possible_cells, self._reduce_single_side(grid, tiles, self.x, self.y+1, 2, 0)))
        return (possible_cells, affected)
    def collapse(self, grid: list[list['Cell']], tiles: dict[str, Tile]) -> list[tuple[int, int]]:
        new_possibles, affected = self.reduce(grid, tiles)
        choosen = random.sample(new_possibles, 1)[0]
        self.possible = [choosen]
        self.collapsed = True
        return affected
            