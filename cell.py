import random
from tile import Tile
class Cell:
    """Represents a Cell of the final picture/grid
    """
    def __init__(self, possible: list, x: int, y: int) -> None:
        """Creates a Cell object

        Args:
            possible (list): a list of possible tile ids this cell can connect to (generally all). Does not need to be prefiltered.
            x (int): the x coordinate in the grid
            y (int): the y coordinate in the grid
        """
        self.possible = possible
        self.collapsed = False
        self.x = x
        self.y = y
    def __str__(self) -> str:
        return f"{str(self.possible)}: {self.collapsed}"
    def __repr__(self) -> str:
        return self.__str__()
    
    def _reduce_single_side(self, grid: list[list['Cell']], tiles: dict[str, Tile], new_x: int, new_y: int, own_side: int, other_side: int) -> list:
        """Return a list of possible cells the given cell can be to, given a side to compare to

        Args:
            grid (list[list[&#39;Cell&#39;]]): The grid containing all cells
            tiles (dict[str, Tile]): all possible tiles
            new_x (int): the x coordinate of the side to compare to
            new_y (int): the y coordinate of the side to compare to
            own_side (int): the own side integer (0 = top, 1 = right, 2 = bottom, 3 = left)
            other_side (int): the other side integer (0 = top, 1 = right, 2 = bottom, 3 = left)

        Returns:
            list: list of all possible tile ids this cell can be, when comparing to another side
        """
        possible_cells = []
        # all possible tiles the other can be
        other_tiles = grid[new_y][new_x].possible
        # all possible side string, the other tiles have connecting to this cell
        other_sockets = list(map(lambda cell: tiles[cell].sides[other_side], other_tiles))
        # for every tile this cell can be
        for self_tile in self.possible:
            # if the reverse of side string of the current tile of this cell is also in the sockets of the other side
            if tiles[self_tile].sides[own_side][::-1] in other_sockets:
                # than this tile is possible to insert
                possible_cells.append(self_tile)
        return possible_cells
    
    def reduce(self, grid: list[list['Cell']], tiles: dict[str, Tile]) -> tuple[set, list[tuple[int, int]]]:
        """Reduces the entropy of this cell by looking at its neighbours and their entropy

        Args:
            grid (list[list[&#39;Cell&#39;]]): the grid containing all cells
            tiles (dict[str, Tile]): all possible tiles

        Returns:
            tuple[set, list[tuple[int, int]]]: a set of all possible tiles, this cell cen be; all neighbours that were compared
        """
        possible_cells = self.possible
        affected = []
        # if not at the edge to the left
        if self.x > 0:
            affected.append((self.x-1, self.y))
            # remove all tiles of possible_cells if they are not in the reduced version for that side
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
        """Determines the new entropy for this cell, then chooses a random tile and collapses the cell

        Args:
            grid (list[list[&#39;Cell&#39;]]): the grid containing all cells
            tiles (dict[str, Tile]): all possible tiles

        Returns:
            list[tuple[int, int]]: list of affected neighbours by this collapse
        """
        new_possibles, affected = self.reduce(grid, tiles)
        choosen = random.sample(new_possibles, 1)[0]
        self.possible = [choosen]
        self.collapsed = True
        return affected
            