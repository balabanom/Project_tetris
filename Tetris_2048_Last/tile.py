import lib.stddraw as stddraw # used for drawing the tiles to display them
from lib.color import Color # used for coloring the tiles
from point import Point
import copy as cp
import math
import numpy as np

# A class for modeling numbered tiles as in 2048
class Tile:
   # Class variables shared among all Tile objects
   # ---------------------------------------------------------------------------
   # the value of the boundary thickness (for the boxes around the tiles)
   boundary_thickness = 0.004
   # font family and size used for displaying the tile number
   font_family, font_size = "Arial", 14

   # A constructor that creates a tile with 2 as the number on it
   def __init__(self, position = Point(0, 0)): # (0, 0) is the default position
      # The random number of the tile 2 or 4 the inital tiles.
      numbers = [2, 4]
      # Sets a background colors with an array.
      self.colors = [Color(239, 230, 221), Color(239, 227, 205), Color(247,178,123), Color(247,150,99), Color(247,124,90),
                Color(247,93,59), Color(239,205,115), Color(239,206,99), Color(239,198,82), Color(238,198,66), Color(239,194,49), Color(60,58,51)]
      self.num = int(np.random.choice(numbers, 1))
      self.number = self.num
      # set the colors of this tile
      self.background_color = self.colors[int(math.log2(self.num))-1] # background (tile) color
      self.foreground_color = Color(0, 100, 200) # foreground (number) color
      self.boundary_color = Color(0, 100, 200) # boundary (box) color

      self.position = Point(position.x, position.y)

   def set_position(self, position):
      self.position = cp.copy(position)

   def get_position(self):
      return cp.copy(self.position)

   def move(self, dx, dy):
      self.position.translate(dx, dy)

   # A method for drawing this tile at a given position with a given length
   def draw(self, position = None):
      if position is None:
          position = self.position
      # draw the tile as a filled square
      stddraw.setPenColor(self.background_color)
      stddraw.filledSquare(self.position.x, self.position.y, 0.5)
      # draw the bounding box around the tile as a square
      stddraw.setPenColor(self.boundary_color)
      stddraw.setPenRadius(Tile.boundary_thickness)
      stddraw.square(self.position.x, self.position.y, 0.5)
      stddraw.setPenRadius()  # reset the pen radius to its default value
      # draw the number on the tile
      stddraw.setPenColor(self.foreground_color)
      stddraw.setFontFamily(Tile.font_family)
      stddraw.setFontSize(Tile.font_size)
      stddraw.boldText(self.position.x, self.position.y, str(self.number))

   # Update color according to the number they have.
   def updateColor(self, num):
      self.background_color = self.colors[int(math.log2(num)) - 1]