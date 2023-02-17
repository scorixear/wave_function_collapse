from PIL import Image
class Tile:
  def __init__(self, img: Image, sides: list):
    self.img: 'Image' = img
    self.sides = sides
    self.id = img.filename.split("\\")[-1].split(".")[0]
  
  def __str__(self):
    return f"{self.id}: {self.sides}"
  def __repr__(self) -> str:
    return self.__str__()