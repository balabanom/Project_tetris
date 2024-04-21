################################################################################
#                                                                              #
# The main program of Tetris 2048 Base Code                                    #
#                                                                              #
################################################################################

import numpy as np
import lib.stddraw as stddraw # for creating an animation with user interactions
from lib.picture import Picture  # used for displaying an image on the game menu
from lib.color import Color  # used for coloring the game menu
import random  # used for creating tetrominoes with random types (shapes)
from game_grid import GameGrid  # the class for modeling the game grid
from tetromino import Tetromino  # the class for modeling the tetrominoes

import os


# Created a class
class Game:
    # Main function where this program starts execution
    def start(self):    
        # set the dimensions of the game grid
        grid_h, grid_w = 20, 20
        # grids for whole table, this game_w is for excld. next tetromino's part
        game_w = 12
        # set the size of the drawing canvas (the displayed window)
        canvas_h, canvas_w = 40 * grid_h, 40 * grid_w
        stddraw.setCanvasSize(canvas_w, canvas_h)
        # set the scale of the coordinate system for the drawing canvas
        stddraw.setXscale(-0.5, grid_w - 0.5)
        stddraw.setYscale(-0.5, grid_h - 0.5)

        # An empty list to store the next 10 tetrominos.
        self.tetrominos = list()
        # # of rounds
        self.round_count = 0
        # Generate 10 tetrominos and store to the array.
        self.create_tetromino(grid_h, game_w)

        # Store next type
        self.next_type = self.tetrominos[self.round_count + 1]
        # Show to the user what the next tetromino is.
        self.next_type.move_pos(15, 15)

        # create the game grid
        grid = GameGrid(grid_h, grid_w)

        # create the first tetromino to enter the game grid
        # by using the create_tetromino function defined below
        current_tetromino = self.tetrominos[self.round_count]
        # To draw first tetromino
        grid.current_tetromino = current_tetromino

        # Game restart
        self.restart = False
        # Game paused
        self.is_paused = False
        # Game finished
        self.is_finished = False
        # Game over
        self.game_over = False

        # display a simple menu before opening the game
        # by using the display_game_menu function defined below
        self.display_game_menu(grid_h, grid_w, grid)
        # the main game loop
        while True:
            # To draw following tetromino
            grid.set_next(self.tetrominos[self.round_count + 1])
            # If the user click the stop button
            if stddraw.mousePressed():
                if stddraw.mouseX() <= 10.5 + 0.6 and stddraw.mouseX() >= 10.5 - 0.6:
                    if stddraw.mouseY() <= 18.5 + 0.6 and stddraw.mouseY() >= 10.8 - 0.6:
                        self.is_paused = True
                        print("Stopped")
                        self.display_game_menu(grid_h, grid_w, grid)

            # check for any user interaction via the keyboard
            if stddraw.hasNextKeyTyped():
                key_typed = stddraw.nextKeyTyped()
                # if the left arrow key has been pressed
                if key_typed == "left":
                    # move the tetromino left by one
                    current_tetromino.move(key_typed, grid)
                # if the right arrow key has been pressed
                elif key_typed == "right":
                    # move the tetromino right by one
                    current_tetromino.move(key_typed, grid)
                # if the down arrow key has been pressed
                elif key_typed == "down":
                    # move the tetromino down by one
                    # (causes the tetromino to fall down faster)
                    current_tetromino.move(key_typed, grid)
                elif key_typed == "up":
                    # rotate the tetromino
                    current_tetromino.rotation(grid, current_tetromino)
                # Additinoal pause options pressing p
                elif key_typed == "p":
                    print("Paused")
                    # pause game
                    self.is_paused = not self.is_paused
                    self.display_game_menu(grid_h, grid_w, grid)

                # clear the queue of the pressed keys for a smoother interaction
                stddraw.clearKeysTyped()

            # Check if is paused?
            if not self.is_paused:
                # if not make down the tetromino
                success = current_tetromino.move("down", grid)

            # lock the active tetromino onto the grid when it cannot go down anymore
            if not success:
                # get the tile matrix of the tetromino without empty rows and columns
                # and the position of the bottom left cell in this matrix
                tiles_to_place = current_tetromino.tile_matrix
                # update the game grid by locking the tiles of the landed tetromino
                self.game_over = grid.update_grid(tiles_to_place)

                # Merge process
                merge = self.check_merging(grid)
                while merge:
                    merge = self.check_merging(grid)

                # To check if rows are full
                row_count = self.is_full(grid_h, grid_w, grid)
                index = 0
                # Shift down the rows.
                while index < grid_h:
                    while row_count[index]:
                        self.slide_down(row_count, grid)
                        row_count = self.is_full(grid_h, grid_w, grid)
                    index += 1

                # Assigns labels to each tile using 4-component labeling
                labels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)
                free_tiles = [[False for v in range(grid_w)] for b in range(grid_h)]
                free_tiles, num_free = self.find_free_tiles(grid_h, grid_w, labels, free_tiles)
                # Drop down the tiles that is free
                grid.move_free_tiles(free_tiles)

                # until no tile to drop down
                while num_free != 0:
                    labels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)
                    free_tiles = [[False for v in range(grid_w)] for b in range(grid_h)]
                    free_tiles, num_free = self.find_free_tiles(grid_h, grid_w, labels, free_tiles)
                    grid.move_free_tiles(free_tiles)

                #klabels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)
                merge = self.check_merging(grid)
                while merge:
                    merge = self.check_merging(grid)

                row_count = self.is_full(grid_h, grid_w, grid)
                index = 0

                while index < grid_h:
                    while row_count[index]:
                        self.slide_down(row_count, grid)
                        row_count = self.is_full(grid_h, grid_w, grid)
                    index += 1

                # Assigns labels to each tile using 4-component labeling
                labels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)
                free_tiles = [[False for v in range(grid_w)] for b in range(grid_h)]
                free_tiles, num_free = self.find_free_tiles(grid_h, grid_w, labels, free_tiles)
                # Drop down the tiles that is free
                grid.move_free_tiles(free_tiles)

                # until no tile to drop down
                while num_free != 0:
                    labels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)
                    free_tiles = [[False for v in range(grid_w)] for b in range(grid_h)]
                    free_tiles, num_free = self.find_free_tiles(grid_h, grid_w, labels, free_tiles)
                    grid.move_free_tiles(free_tiles)

                #labels, num_labels = self.connected_component_labeling(grid.tile_matrix, grid_w, grid_h)

                # end the main game loop if the game is over
                if self.game_over:
                    print("Game Over")
                    self.is_finished = True
                    self.display_game_menu(grid_h, grid_w, grid)

                self.round_count += 1

                # create the next tetromino to enter the game grid
                # by using the create_tetromino function defined below
                current_tetromino = self.tetrominos[self.round_count]
                grid.current_tetromino = current_tetromino
                # Random position the tetromino
                new_x, new_y = random.randint(2, 9), 21
                current_tetromino.move_pos(new_x, new_y)

                # Empty the list and put new tetrominos
                if self.round_count == 8:
                    self.tetrominos = list()
                    self.round_count = 0
                    self.create_tetromino(grid_h, game_w)
                # Show next tetromino
                self.next_type = self.tetrominos[self.round_count+1]
                self.next_type.move_pos(15, 15)

            # In case restarting game, clear places with nonetype.
            if self.restart:
                for a in range(0, 20):
                    for b in range(12):
                        grid.tile_matrix[a][b] = None
                self.restart = False
                grid.game_over = False
                current_tetromino = self.tetrominos[self.round_count]
                grid.current_tetromino = current_tetromino
                new_x, new_y = random.randint(2, 9), 22
                current_tetromino.move_pos(new_x, new_y)

            # display the game grid with the current tetromino
            grid.display()

    # Checks if there is tile to merge.
    def check_merging(self, grid):
        merged = False
        for a in range(0, 19):
            for b in range(12):
                # If there is a tile above
                if grid.tile_matrix[a][b] != None and grid.tile_matrix[a + 1][b] != None:
                    # If two tiles numbers are equal
                    if grid.tile_matrix[a][b].number == grid.tile_matrix[a + 1][b].number:
                        # Delete the above tile
                        grid.tile_matrix[a + 1][b].set_position(None)
                        grid.tile_matrix[a + 1][b] = None
                        # Update the number of below tile
                        grid.tile_matrix[a][b].number += grid.tile_matrix[a][b].number
                        # Update the score
                        grid.score += grid.tile_matrix[a][b].number
                        # To change the game speed.
                        grid.last_updated += grid.tile_matrix[a][b].number
                        # Change color
                        grid.tile_matrix[a][b].updateColor(grid.tile_matrix[a][b].number)
                        merged = True
        return merged

    # If row is full return True, else False
    def is_full(self, grid_h, grid_w, grid):
        # At the beginning, all is false.
        row_count = [False for i in range(grid_h)]
        # score if row is full
        score = 0
        for h in range(grid_h):
            # counter = 12 that means row is full in our grid.
            counter = 0
            for w in range(grid_w):
                if grid.is_occupied(h, w):
                    counter += 1
                # If row is full, calculate score.
                if counter == 12:
                    score = 0
                    for a in range(12):
                        score += grid.tile_matrix[h][a].number
                    row_count[h] = True
        # Update the score
        grid.score += score
        # Update game speed if needed.
        grid.last_updated += score
        return row_count

    def slide_down(self, row_count, grid):
        for index, i in enumerate(row_count):
            if i:
                for a in range(index, 19):
                    row = np.copy(grid.tile_matrix[a + 1])
                    grid.tile_matrix[a] = row
                    for b in range(12):
                        if grid.tile_matrix[a][b] is not None:
                            grid.tile_matrix[a][b].move(0, -1)
                break

    # A function for creating random shaped tetrominoes to enter the game grid
    def create_tetromino(self, grid_height, grid_width):
        self.rotated = False
        # type (shape) of the tetromino is determined randomly
        tetromino_types = ['I', 'O', 'Z', 'J', 'L', 'T', 'S']
        for i in range(10):
            random_index = random.randint(0, len(tetromino_types) - 1)
            self.random_type = tetromino_types[random_index]
            # create and return the tetromino
            tetromino = Tetromino(self.random_type, grid_height, grid_width)
            self.tetrominos.append(tetromino)
        # return self.tetrominos  # not necessary, the function is updated.

    # A function for displaying a simple menu before starting the game
    def display_game_menu(self, grid_height, grid_width, grid):
         #the colors used for the menu
        background_color = Color(42, 69, 99)
        button_color = Color(25, 255, 228)
        text_color = Color(31, 160, 239)
        # clear the background canvas to background_color
        stddraw.clear(background_color)
        # get the directory in which this python code file is placed
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # compute the path of the image file
        img_file = current_dir + "/menu_image.png"
        # the coordinates to display the image centered horizontally
        img_center_x, img_center_y = (grid_width - 1) / 2, grid_height - 7
        # the image is modeled by using the Picture class
        image_to_display = Picture(img_file)
        # add the image to the drawing canvas
        stddraw.picture(image_to_display, img_center_x, img_center_y)
        # the dimensions for the start game button
        button_w, button_h = grid_width - 1.5, 2
        # the coordinates of the bottom left corner for the start game button
        button_blc_x, button_blc_y = img_center_x - button_w / 2, 4
        # add the start game button as a filled rectangle
        stddraw.setPenColor(button_color)
        stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)
        # add the text on the start game button
        stddraw.setFontFamily("Arial")
        stddraw.setFontSize(25)
        stddraw.setPenColor(text_color)

        # If game paused
        if not self.is_finished and self.is_paused:
            stddraw.setPenColor(button_color)
            button2_blc_x, button2_blc_y = img_center_x - button_w / 2, 1
            stddraw.filledRectangle(button_blc_x, button_blc_y - 3, button_w, button_h)
            stddraw.setFontFamily("Arial")
            stddraw.setFontSize(25)
            stddraw.setPenColor(text_color)

            text_to_display = "Continue"
            stddraw.text(img_center_x, 5, text_to_display)

            text1_to_display = "Restart"
            stddraw.text(img_center_x, 2, text1_to_display)
            # the user interaction loop for the simple menu
            while True:
                # display the menu and wait for a short time (50 ms)
                stddraw.show(50)
                # check if the mouse has been left-clicked on the start game button
                if stddraw.mousePressed():
                    # get the coordinates of the most recent location at which the mouse
                    # has been left-clicked
                    mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
                    # Close menu
                    if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
                        if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
                            self.is_paused = False
                            break
                        # Restart the game
                        elif mouse_y >= button2_blc_y and mouse_y <= button2_blc_y + button_h:
                            self.is_paused = False
                            grid.score = 0
                            self.restart = True
                            grid.speed_increased_counter = 0
                            # Choice to game speed
                            self.speed_screen(grid, background_color, grid_width, grid_height, img_file, button_color)
                            break

        # If game is finished, restart a new one
        elif self.is_finished:
            stddraw.setPenColor(Color(25, 255, 228))
            stddraw.text(img_center_x, 8, "Game Over")
            stddraw.setPenColor(text_color)
            text1_to_display = "Restart"
            stddraw.text(img_center_x, 5, text1_to_display)
            while True:
                stddraw.show(50)
                if stddraw.mousePressed():

                    mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
                    if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
                        if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
                            self.restart = True
                            grid.speed_increased_counter = 0
                            self.is_paused = False
                            self.is_finished = False
                            self.game_over = False
                            # reset score
                            grid.score = 0

                            self.speed_screen(grid, background_color, grid_width, grid_height, img_file, button_color)
                            break

        else:
            text1_to_display = "Start Game"
            stddraw.text(img_center_x, 5, text1_to_display)
            while True:
                stddraw.show(50)
                if stddraw.mousePressed():
                    mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
                    if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
                        if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
                            text1_to_display = "Start Game"
                            stddraw.text(img_center_x, 5, text1_to_display)
                            break

            self.speed_screen(grid, background_color, grid_width, grid_height, img_file, button_color)


    # Game speed section, slow normal fast
    def speed_screen(self, grid, background_color, grid_width, grid_height, img_file, button_color):
        stddraw.clear(background_color)
        # image coord.
        img_center_x, img_center_y = (grid_width - 1) / 2, grid_height - 7
        image_to_display = Picture(img_file)
        # picture the image
        stddraw.picture(image_to_display, img_center_x, img_center_y)
        # start game button dimensions
        button_w, button_h = grid_width - 17, 2
        stddraw.setPenColor(button_color)
        # blc of the start game button
        button1_blc_x, button1_blc_y = img_center_x - button_w / 2, 4
        button2_blc_x, button2_blc_y = button1_blc_x - 5, 4
        button3_blc_x, button3_blc_y = button1_blc_x + 5, 4
        stddraw.filledRectangle(button1_blc_x, button1_blc_y, button_w, button_h)
        stddraw.filledRectangle(button2_blc_x, button2_blc_y, button_w, button_h)
        stddraw.filledRectangle(button3_blc_x, button3_blc_y, button_w, button_h)
        stddraw.setPenColor(Color(232, 38, 38))

        normal_speed_text = "Normal"
        stddraw.text(img_center_x, 5, normal_speed_text)

        fast_speed_text = "Slow"
        stddraw.text(img_center_x - 5, 5, fast_speed_text)

        text_to_display = "Fast"
        stddraw.text(img_center_x + 5, 5, text_to_display)

        while True:
            stddraw.show(50)
            if stddraw.mousePressed():
                mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
                print(mouse_x)
                print(button1_blc_x)

                print(button1_blc_x + button_w)
                if mouse_x >= button1_blc_x and mouse_x <= button1_blc_x + button_w:
                    if mouse_y >= button1_blc_y and mouse_y <= button1_blc_y + button_h:
                        print("Normal speed")
                        grid.game_speed = 175
                        break
                if mouse_x >= button2_blc_x and mouse_x <= button2_blc_x + button_w:
                    if mouse_y >= button2_blc_y and mouse_y <= button2_blc_y + button_h:
                        print("Slow speed")
                        grid.game_speed = 250
                        break
                if mouse_x >= button3_blc_x and mouse_x <= button3_blc_x + button_w:
                    if mouse_y >= button3_blc_y and mouse_y <= button3_blc_y + button_h:
                        print("Fast speed")
                        grid.game_speed = 120
                        break

    def connected_component_labeling(self, grid, grid_w, grid_h):
        # Initially, all pixels are assigned the label 0
        labels = np.zeros([grid_h, grid_w], dtype=int)
        min_equivalent_labels = []  # List to store minimum equivalent labels
        current_label = 1  # Current label counter
        for y in range(grid_h):
            for x in range(grid_w):
                if grid[y, x] is None:
                    continue
                # Retrieve neighbor labels of the current pixel
                neighbor_labels = self.get_neighbor_labels(labels, (x, y))
                # If the pixel has no non-empty neighbors
                if len(neighbor_labels) == 0:
                    # Assign the current label to the pixel and increment the current label counter
                    labels[y, x] = current_label
                    current_label += 1
                    # Initially, the minimum equivalent label is the pixel's own label
                    min_equivalent_labels.append(labels[y, x])
                # If there is at least one non-empty neighbor
                else:
                    # Assign the minimum neighbor label to the pixel
                    labels[y, x] = min(neighbor_labels)
                    # Check for conflicts if there are multiple different neighbor labels
                    if len(neighbor_labels) > 1:
                        labels_to_merge = set()
                        # Populate a set with the minimum equivalent label for each neighbor
                        for l in neighbor_labels:
                            labels_to_merge.add(min_equivalent_labels[l - 1])
                        # Update minimum equivalent labels related to the conflict
                        self.update_min_equivalent_labels(min_equivalent_labels, labels_to_merge)
        # Second pass to rearrange equivalent labels consecutively
        self.rearrange_min_equivalent_labels(min_equivalent_labels)
        # Assign final labels to pixels based on minimum equivalent labels
        for y in range(grid_h):
            for x in range(grid_w):
                if grid[y, x] is None:
                    continue
                labels[y, x] = min_equivalent_labels[labels[y, x] - 1]
        return labels, len(set(min_equivalent_labels))

    def get_neighbor_labels(self, label_values, pixel_indices):
        x, y = pixel_indices
        # Set to store unique neighbor labels
        neighbor_labels = set()
        # Include upper pixel if it exists and is non-empty
        if y != 0:
            u = label_values[y - 1, x]
            if u != 0:
                neighbor_labels.add(u)
        # Include left pixel if it exists and is non-empty
        if x != 0:
            l = label_values[y, x - 1]
            if l != 0:
                neighbor_labels.add(l)
        return neighbor_labels

    def update_min_equivalent_labels(self, all_min_eq_labels, min_eq_labels_to_merge):
        # Determine the smallest value among conflicting neighbor labels
        min_value = min(min_eq_labels_to_merge)
        # Update minimum equivalent labels
        for index in range(len(all_min_eq_labels)):
            if all_min_eq_labels[index] in min_eq_labels_to_merge:
                all_min_eq_labels[index] = min_value

    def rearrange_min_equivalent_labels(self, min_equivalent_labels):
        # Sort and assign consecutive values to minimum equivalent labels
        different_labels = set(min_equivalent_labels)
        different_labels_sorted = sorted(different_labels)
        new_labels = np.zeros(max(min_equivalent_labels) + 1, dtype=int)
        count = 1
        for l in different_labels_sorted:
            new_labels[l] = count
            count += 1
        for ind in range(len(min_equivalent_labels)):
            old_label = min_equivalent_labels[ind]
            new_label = new_labels[old_label]
            min_equivalent_labels[ind] = new_label
    def find_free_tiles(self, grid_h, grid_w, labels, free_tiles):
        counter = 0
        free_labels = []
        for x in range(grid_h):
            for y in range(grid_w):
                if labels[x, y] != 1 and labels[x, y] != 0:
                    if x == 0:
                        free_labels.append(labels[x, y])
                    if not free_labels.count(labels[x, y]):
                        free_tiles[x][y] = True
                        counter += 1
        return free_tiles, counter

game = Game()
game.start()