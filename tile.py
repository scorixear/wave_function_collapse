from PIL import Image
class Tile:
    """Represents a single Tile image and their sides that they can connect to
    """
    def __init__(self, img: Image, sides: list):
        """Returns a Tile object
  
        Args:
            img (Image): the image this tile represents
            sides (list): the sides this tile has. Denote the sides by reading iterativly around the tile - meaning Bottom Side should be reversed (right to left)
        """
        self.img: 'Image' = img
        self.sides = sides
        # the id is the name without the file type
        self.id = img.filename.split("\\")[-1].split(".")[0]
    
    def __str__(self):
        return f"{self.id}: {self.sides}"
    def __repr__(self) -> str:
        return self.__str__()