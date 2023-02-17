import os # used for reading in tile files
import json # used for reading in data.json files
import random # used for generatin random numbers
from collections import deque # used rotating arrays of sides
from PIL import Image # used for reading in and displaying the result image
from tile import Tile # represents a tile and its possible sides
from cell import Cell # represents a cell inside the final image

# local directory to the tile-images and data.json
IMG_DIRECTORY ="tiles/circuit"
# how many columns/rows in the final image
DIMENSION = 60
# size of the final image
SIZE=1920

def read_files(directory: str) -> dict[str, Tile]:
    """Reads in tile images and their respective data

    Args:
        directory (str): the directory the images and data.json are contained in (local)

    Returns:
        dict[str, Tile]: dictionary containing each Tile object and their sides, key is the Tile.id
    """
    tiles: dict[str, Tile] = {}
    # read in the data.json file
    with open(os.path.join(directory, "data.json"), "r", encoding="UTF-8") as reader:
        data = json.load(reader)
    # for every file in the given directory
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # if that file is not data.json
        if os.path.isfile(f) and not f.endswith(".json"):
            # retrieve the name of the tile
            name = filename.split(".")[0]
            # load the image
            img = Image.open(f)
            # create the Tile object
            tile = Tile(img, data[name])
            # set it into the output
            tiles[tile.id] = tile
            # for every rotation this tile could be rotated (and would result in new tiles)
            for rotation in data['rotations'][name]:
                # rotate the image clockwise
                newImg = img.rotate(rotation*-90)
                # add the rotation index to the file name (and hence the id)
                newImg.filename = f"{img.filename.split('.')[0]}{rotation}.png"
                # rotate the sides clockwise
                newSides = deque(data[name])
                newSides.rotate(rotation)
                # create new rotated tile
                rotatedTile = Tile(newImg, list(newSides))
                # add to the mix
                tiles[rotatedTile.id] = rotatedTile
    return tiles

def get_lowest_entropy_cells(grid: list[list[Cell]]) -> list[Cell]:
    """Returns a list of cells that have the lowest entropy

    Args:
        grid (list[list[Cell]]): the grid containing all cells

    Returns:
        list[Cell]: the list of cells with lowest entropy
    """
    # current maximum amount of tiles is set to 1000
    # good luck creating a data.json for a tile set of more then 1000 pieces
    current_Lowest = 1000
    collection = []
    # for every cell
    for row in grid:
        for cell in row:
            # if cell can still be collapsed and has lower entropy
            if cell.collapsed is False and len(cell.possible) < current_Lowest:
                # create new list (deleting the old list, since we have a new minimum)
                collection = [cell]
                current_Lowest = len(cell.possible)
            # if cell can still be collapsed and has the current lowest entropy
            elif cell.collapse is False and len(cell.possible) == current_Lowest:
                collection.append(cell)
    return collection

def update_cells(grid: list[list[Cell]], tiles: dict[str, Tile], affected: list[tuple[int, int]], start: Cell) -> list[Cell]:
    """Propagates the changes given by the single collapsed cell through the grid

    Args:
        grid (list[list[Cell]]): the grid containing all tiles
        tiles (dict[str, Tile]): the possible tiles in general
        affected (list[tuple[int, int]]): list of integer coordinates that are affected by the given collapsed cell
        start (Cell): the cell that collapsed

    Returns:
        list[Cell]: the cells that also collapsed during the process
    """
    # the queue is filled with all cells that are affected by the collapse of the starting cell
    queue = affected
    # done cells are cells, that collapsed (and do not need to be checked)
    done = [(start.x, start.y)]
    # collapsed cells is the final output, all cells that collapsed
    collapsed_cells = [start]
    # go through the queue
    while len(queue) > 0:
        # pop the first element
        next_coords = queue.pop(0)
        # if the current cell collapsed in on of the previous steps, do not calculate (since it cannot be more collapsed)
        if next_coords not in done:
            # retrieve the Cell object for the given coordinates
            next_cell: Cell = grid[next_coords[1]][next_coords[0]]
            # if that cell is collapsed (collapsed by a previous call of this function, but not in done yet)
            if next_cell.collapsed:
                # add it to done and skip the calculation
                done.append(next_coords)
                continue
            # reduce the entropy of this cell by looking at its neighbours, returns a list of affected neighbours if this entropy changed
            # this is generally 4 members (4 sides of a tile) except at the edges
            new_possibles, affected = next_cell.reduce(grid, tiles)
            # if the entropy did not get reduced - skip next steps
            # entropies never change and have the same length as only entropies are removed, never added
            # this cell might be affected by other cells and their reduced entropy, hence we don't add it to "done"
            if len(next_cell.possible) == len(new_possibles):
                continue
            # go through all affected neighbours
            for aff in affected:
                # if the neighbour is already collapsed or already in queue, skip
                if aff not in done and aff not in queue:
                    queue.append(aff)
            # set the new entropy for this cell
            next_cell.possible = new_possibles
            # if the new entropy collapsed this cell
            if len(new_possibles) == 1:
                # set their properties, add to output and done
                next_cell.collapsed = True
                collapsed_cells.append(next_cell)
                done.append(next_coords)
    return collapsed_cells

def draw_canvas(canvas_grid: list[list[Tile]]):
    """Draws a given grid of tiles to the screen

    Args:
        canvas_grid (list[list[Tile]]): the grid of tiles. If no tile was set yet, the tile should be None
    """
    # create Canvas of given size
    canvas = Image.new('RGB', (SIZE,SIZE),0)
    tile_size = SIZE//DIMENSION
    
    # for all tiles in the grid
    for j, row in enumerate(canvas_grid):
        for i, tile in enumerate(row):
            # if the tile is set
            if tile is not None:
                # add the tile image to the final canvas
                canvas.paste(tile.img.resize((tile_size, tile_size), Image.ANTIALIAS), (i*tile_size, j*tile_size))
    
    canvas.save(f"output\\{IMG_DIRECTORY.split('/')[1]}.png")
    canvas.show()

def main():
    # read in tiles
    tiles: dict[str, Tile] = read_files(IMG_DIRECTORY)
    
    # generate two-dimensional grid of Cell objects, set their current entropy to all possible tiles and set their x and y position
    grid = [[Cell(list(map(lambda tile: tile, tiles)), j, i) for j in range(DIMENSION)] for i in range(DIMENSION)]
    # generate canvas grid (grid of tiles later drawn) with no tiles set
    canvas_grid = [[None for _ in range(DIMENSION)] for _ in range(DIMENSION)]
    
    # retrieve current cells that have lowest entropy (Should be all cells)
    new_choose = get_lowest_entropy_cells(grid)
    
    # the counter depicts how many tiles were set
    # if get_lowest_entropy_cells does not find new cells, this means we ran into a dead end
    counter = 0
    # while we found new tiles with lower entropy (should be only if all tiles are set)
    while len(new_choose) > 0:
        # retrieve a random cell with lowest entropy
        next_cell: Cell = random.sample(new_choose, 1)[0]
        # collapse the cell and return its affected neighbours (generally 4, at the edge 2 or 3)
        affected = next_cell.collapse(grid, tiles)
        
        # propagate the collapse through the grid. This could collapse other cells (very uncommon, depends on what cells we collapsed)
        # Example of a situation where a new cell is also collapsed:
        # |   |   |   |   |   |
        # |   |   | # |   |   |   A non-collapsed cell C is surrounded by already collapsed cell #
        # |   | + | C | # |   |   The above collapse function collapsed cell +
        # |   |   | # |   |   |   With a small Tile set, this could mean only 1 possible Tile fits (or none)
        # |   |   |   |   |   |   Hence the cell collapses
        collapsed: list[Cell] = update_cells(grid, tiles, affected, next_cell)
        # for every collapsed cell
        for cell in collapsed:
            # update the canvas grid with the given cell tile it collapsed to
            # this should throw an error, if the collapse resulted in 0 possibilities
            canvas_grid[cell.y][cell.x] = tiles[cell.possible[0]]
            # update the counter, since we added an additional tile
            counter += 1
        # and choose the next lowest entropy cells
        new_choose = get_lowest_entropy_cells(grid)
    # after collapsing all possible cells with the given randomization, draw the graph
    draw_canvas(canvas_grid)
    # if we could not find additional low-entropy cells, but did not fill the grid, we are in trouble
    if counter < DIMENSION*DIMENSION:
        print("No combination found")
    
if __name__ == "__main__":
    main()
