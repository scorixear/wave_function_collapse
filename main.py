import os
import json
import random
from collections import deque
from PIL import Image
from tile import Tile
from cell import Cell

IMG_DIRECTORY ="tiles/circuit_coding_train"
DIMENSION = 40
SIZE=1920

def read_files(directory) -> dict[str, Tile]:
    tiles = {}
    with open(os.path.join(directory, "data.json"), "r", encoding="UTF-8") as reader:
        data = json.load(reader)
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f) and not f.endswith(".json"):
            name = filename.split(".")[0]
            img = Image.open(f)
            tile = Tile(img, data[name])
            tiles[tile.id] = tile
            for rotation in data['rotations'][name]:
                newImg = img.rotate(rotation*-90)
                newImg.filename = f"{img.filename.split('.')[0]}{rotation}.png"
                newSides = deque(data[name])
                newSides.rotate(rotation)
                rotatedTile = Tile(newImg, list(newSides))
                tiles[rotatedTile.id] = rotatedTile
    return tiles

def get_lowest_entropy_cells(grid: list[list[Cell]]) -> list[Cell]:
    current_Lowest = 1000
    collection = []
    for row in grid:
        for cell in row:
            if cell.collapsed is False and len(cell.possible) < current_Lowest:
                collection = [cell]
                current_Lowest = len(cell.possible)
            elif len(cell.possible) == current_Lowest:
                collection.append(cell)
    return collection

def update_cells(grid: list[list[Cell]], tiles: dict[str, Tile], affected: list[tuple[int, int]], start: Cell):
    queue = affected
    done = [(start.x, start.y)]
    collapsed_cells = [start]
    while len(queue) > 0:
        next_coords = queue.pop(0)
        if next_coords not in done:
            next_cell: Cell = grid[next_coords[1]][next_coords[0]]
            if next_cell.collapsed:
                done.append(next_coords)
                continue
            new_possibles, affected = next_cell.reduce(grid, tiles)
            if len(next_cell.possible) == len(new_possibles):
                continue
            for aff in affected:
                if aff not in done and aff not in queue:
                    queue.append(aff)
            next_cell.possible = new_possibles
            if len(new_possibles) == 1:
                next_cell.collapsed = True
                collapsed_cells.append(next_cell)
                done.append(next_coords)
    return collapsed_cells

def draw_canvas(canvas_grid: list[list[Tile]]):
    canvas = Image.new('RGB', (SIZE,SIZE),0)
    tile_size = SIZE//DIMENSION
    
    for j, row in enumerate(canvas_grid):
        for i, tile in enumerate(row):
            if tile is not None:
                canvas.paste(tile.img.resize((tile_size, tile_size), Image.ANTIALIAS), (i*tile_size, j*tile_size))
    canvas.show()

def main():
    tiles = read_files(IMG_DIRECTORY)
    
    #rand_seed = "demo"
    #random.seed(rand_seed)
    
    grid = [[Cell(list(map(lambda tile: tile, tiles)), j, i) for j in range(DIMENSION)] for i in range(DIMENSION)]
    canvas_grid = [[None for _ in range(DIMENSION)] for _ in range(DIMENSION)]
    #print(grid)
    
    new_choose = get_lowest_entropy_cells(grid)
    
    counter = 0
    while len(new_choose) > 0:
        next_cell: Cell = random.sample(new_choose, 1)[0]
        affected = next_cell.collapse(grid, tiles)
        collapsed: list[Cell] = update_cells(grid, tiles, affected, next_cell)
        for cell in collapsed:
            canvas_grid[cell.y][cell.x] = tiles[cell.possible[0]]
            counter += 1
        
        new_choose = get_lowest_entropy_cells(grid)
    draw_canvas(canvas_grid)
    if counter < DIMENSION*DIMENSION:
        print("No combination found")
    
  

if __name__ == "__main__":
  main()