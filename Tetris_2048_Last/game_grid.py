import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
import numpy as np  # fundamental Python module for scientific computing
import copy
from point import Point  # used for tile positions

# A class for modeling the game grid
class GameGrid:
    # A constructor for creating the game grid based on the given arguments
    def __init__(self, grid_h, grid_w):
        # set the dimensions of the game grid as the given arguments
        self.grid_height = grid_h
        self.grid_width = grid_w
        # create a tile matrix to store the tiles locked on the game grid
        self.tile_matrix = np.full((grid_h, grid_w), None)
        # create the tetromino that is currently being moved on the game grid
        self.current_tetromino = None
        # the game_over flag shows whether the game is over or not
        self.game_over = False
        # set the color used for the empty grid cells
        self.empty_cell_color = Color(200, 200, 200)
        # set the colors used for the grid lines and the grid boundaries
        self.line_color = Color(0, 100, 200)
        self.boundary_color = Color(0, 100, 200)
        # thickness values used for the grid lines and the grid boundaries
        self.line_thickness = 0.004
        self.box_thickness = 8 * self.line_thickness
        # Game score
        self.score = 0

        self.pos = Point()
        # Default game speed
        self.game_speed = 250
        # To update speed according to the score
        self.last_updated = 0
        # How many times speed increased?
        self.incr_counter = 0

    # A method for displaying the game grid
    def display(self):
        # check score > 500, then increased the speed.
        self.change_speed()
        # clear the background to empty_cell_color
        stddraw.clear(self.empty_cell_color)
        # draw the game grid
        self.draw_grid()
        # draw the current/active tetromino if it is not None
        # (the case when the game grid is updated)
        # Additional we have to check next_tetromino and draw it.
        if self.current_tetromino is not None and self.next_tetromino is not None:
            self.current_tetromino.draw()
            self.next_tetromino.draw()

        # draw a box around the game grid
        self.draw_boundaries()
        # show the resulting drawing with a pause duration = game_speed ms
        stddraw.show(self.game_speed)

    # A method for drawing the cells and the lines of the game grid
    def draw_grid(self):
        # for each cell of the game grid
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # if the current grid cell is occupied by a tile
                if self.tile_matrix[row][col] is not None:
                    # draw this tile
                    self.tile_matrix[row][col].draw()

        # Drawing the stop button
        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.filledRectangle(10.5, 18.5, .6, .6)
        stddraw.setPenRadius(100)
        stddraw.setPenColor(Color(255, 255, 255))
        stddraw.text(10.8, 18.8, "Stop")

        self.drawScore(self.score)
        self.display_info("Speed Increased", self.incr_counter)

        # inner lines of the game grid
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)

        # ranges for the game grid
        start_x, end_x = -0.5, 12 - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
            stddraw.line(x, start_y, x, end_y)
        for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # A method for drawing the boundaries around the game grid
    def draw_boundaries(self):
        # draw a bounding box around the game grid as a rectangle
        stddraw.setPenColor(self.boundary_color)  # using boundary_color
        # set the pen radius as box_thickness (half of this thickness is visible
        # for the bounding box as its lines lie on the boundaries of the canvas)
        stddraw.setPenRadius(self.box_thickness)
        # the coordinates of the bottom left corner of the game grid
        pos_x, pos_y = -0.5, -0.5
        stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # A method used for checking whether the grid cell with given row and column
    # indexes is occupied by a tile or not (i.e., empty)
    def is_occupied(self, row, col):
        # considering the newly entered tetrominoes to the game grid that may
        # have tiles with position.y >= grid_height
        if not self.is_inside(row, col):
            return False # the cell is not occupied as it is outside the grid
        # the cell is occupied by a tile if it is not None
        return self.tile_matrix[row][col] != None

    # A method used for checking whether the cell with given row and column indexes
    # is inside the game grid or not
    def is_inside(self, row, col):
        if row < 0 or row >= self.grid_height:
            return False
        if col < 0 or col >= self.grid_width:
            return False
        return True

    # A method that locks the tiles of a landed tetromino on the grid checking
    # if the game is over due to having any tile above the topmost grid row.
    # return True game is over, False otherwise.)
    def update_grid(self, tiles_to_place):
        # lock the tiles of the current tetromino (tiles_to_lock) on the grid
        n_rows, n_cols = len(tiles_to_place), len(tiles_to_place[0])
        for col in range(n_cols):
            for row in range(n_rows):
                # place each tile (occupied cell) onto the game grid
                if tiles_to_place[row][col] != None:
                    pos = tiles_to_place[row][col].get_position()
                    if self.is_inside(pos.y, pos.x):
                        self.tile_matrix[pos.y][pos.x] = tiles_to_place[row][col]
                    # the game is over if any placed tile is out of the game grid
                    else:
                        self.game_over = True
        # return the value of the game_over flag
        return self.game_over

    # Moves the list of free tiles (tiles not connected to others) one unit downward.
    def move_free_tiles(self, free_tiles):
        for row in range(self.grid_height - 1):  # excluding the bottommost row
            for col in range(self.grid_width):
                if free_tiles[row][col]:
                    free_tile_copy = copy.deepcopy(self.tile_matrix[row][col])
                    self.tile_matrix[row - 1][col] = free_tile_copy
                    dx, dy = 0, -1  # change of position in x and y directions
                    self.tile_matrix[row - 1][col].move(dx, dy)
                    self.tile_matrix[row][col] = None

    # Draws the main score at the top right of the main game screen.
    def drawScore(self, score=0):
        stddraw.setPenRadius(150)
        stddraw.setPenColor(Color(255, 255, 255))
        text_to_display = "Score: " + str(score)
        stddraw.text(15.8, 18.8, text_to_display)

    # Sets the following tetromino from the Game object to the right side.
    def set_next(self, next_tetromino):
        self.next_tetromino = next_tetromino

    # Displays the given information text on the screen along with a count.
    def display_info(self, txt, count):
        stddraw.setPenRadius(150)
        stddraw.setPenColor(Color(255, 255, 255))
        stddraw.setFontSize(20)
        text = str(txt) + " x " + str(count)
        stddraw.text(15.8, 18, text)
        stddraw.text(15.8, 16.5, "Next Tetromino:")

    # Increases the game speed based on the total score, by 50 units for every 500 score.
    # The speed doesn't change if it's already less than 50.
    def change_speed(self):
        if self.last_updated > 500 and self.game_speed >= 50:
            rate = int(self.game_speed * 0.05)
            print("Previous Speed:", self.game_speed)
            self.game_speed -= rate
            print("New Speed:", self.game_speed)
            self.incr_counter += 1
            self.last_updated = self.score % 500