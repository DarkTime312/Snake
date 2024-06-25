import customtkinter as ctk
from settings import *
from random import randint
import logging
from util import LimitedList


class Snake(ctk.CTk):
    def __init__(self):
        super().__init__()

        # window setup
        self.title('Snake')
        self.geometry(f'{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}')
        # Configure the grid layout for the window
        self.grid_window()
        # Initialize the starting direction of the snake
        self.direction = 'right'
        # Bind keyboard arrow keys to change the snake's direction
        self.bind_keyboard()

        # Create the apple frame and randomize its position on the grid
        self.apple = ctk.CTkFrame(self, fg_color=APPLE_COLOR)
        self.randomize_apple_position()

        # Set the initial refresh speed for the snake's movement
        self.refresh_speed = 250
        # Set the initial length of the snake's tail
        self.snake_tail_length = 3

        # Initialize the starting position of the snake's head
        self.row = START_POS[1]
        self.column = START_POS[0]
        # Create a limited list to store the snake's body parts
        self.body_positions = LimitedList(3)
        self.body_objects = []

        # Create the snake's head frame and place it on the grid
        self.snake_head = ctk.CTkFrame(self, fg_color=SNAKE_HEAD_COLOR, corner_radius=0)

        # Add initial body parts to the snake's body list
        self.body_objects.append(ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0))
        self.body_objects.append(ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0))

        self.body_positions.add((self.row, self.column - 2))
        self.body_positions.add((self.row, self.column - 1))
        self.body_positions.add((self.row, self.column))

        self.body_objects[0].grid(row=self.row, column=self.column - 2)
        self.body_objects[1].grid(row=self.row, column=self.column - 1)

        self.snake_head.grid(row=self.row, column=self.column)

        # Start the snake's movement
        self.movement()

    def bind_keyboard(self):
        """
        Binds keyboard arrow keys to the snake's direction change events.

        This method binds the Up, Down, Left, and Right arrow keys to the corresponding
        direction change events for the snake. When an arrow key is pressed, the snake's
        direction is updated accordingly:

        - Up arrow key changes the direction to 'up'.
        - Down arrow key changes the direction to 'down'.
        - Left arrow key changes the direction to 'left'.
        - Right arrow key changes the direction to 'right'.

        :return: None
        """
        self.bind('<Up>', lambda e: self.change_direction(e, 'up'))
        self.bind('<Down>', lambda e: self.change_direction(e, 'down'))
        self.bind('<Left>', lambda e: self.change_direction(e, 'left'))
        self.bind('<Right>', lambda e: self.change_direction(e, 'right'))

    def randomize_apple_position(self):
        """
        Randomizes the position of the apple on the grid.

        This method generates a random position for the apple within the bounds of the grid
        defined by the `FIELDS` constant. The apple's row and column indices are set to random
        values within the allowable range, and the apple is placed at the new position on the grid.
        The new position of the apple is also logged for debugging purposes.

        :return: None
        """

        # creating a random apple
        max_row_index = FIELDS[1] - 1
        max_column_index = FIELDS[0] - 1

        self.apple_row = randint(0, max_row_index)
        self.apple_column = randint(0, max_column_index)
        self.apple.grid(row=self.apple_row, column=self.apple_column)

    def grid_window(self):
        """
        Configures the grid layout for the window.

        This method sets up the grid layout for the window by configuring the rows and columns
        based on the number of rows and columns specified in the `FIELDS` constant. Each row and
        column is configured to have an equal weight and uniform size, ensuring that the grid
        cells are evenly distributed across the window.

        :return: None
        """
        number_of_rows = FIELDS[1]
        number_of_columns = FIELDS[0]
        # creating the rows
        for index in range(number_of_rows):
            self.rowconfigure(index, weight=1, uniform='a')

        # creating the columns
        for index in range(number_of_columns):
            self.columnconfigure(index, weight=1, uniform='a')

    def movement(self):
        """
        Handles the movement of the snake in the game.

        This method updates the position of the snake's head based on the current direction of movement.
        It checks for collisions with the apple, updates the snake's body parts, and schedules the next
        movement. If the game is over, it displays a "Game Over" message.

        The following steps are performed in this method:

        1. Update the snake's head position based on the current direction.
        2. Check if the game is still on by calling `self.game_on()`.
        3. If the game is on:
           a. Handle collisions with the apple by calling `self.handle_apple_collision()`.
           b. Log the current grid layout and the new position of the snake's head.
           c. Update the grid to reflect the new position of the snake's head.
           d. Remove the tail part from the grid.
           e. Add the new head position to the snake's body list.
           f. Log the body parts after movement.
           g. Schedule the next movement using `self.after(self.refresh_speed, self.movement)`.
        4. If the game is over:
           a. Display a "Game Over" message with the snake's tail length as the record.
           b. Log the "Game Over" message.

        :return: None
        """

        current_direction = self.direction
        old_row = self.row
        old_column = self.column

        self.row += DIRECTIONS.get(current_direction)[1]
        self.column += DIRECTIONS.get(current_direction)[0]
        if self.game_on():
            self.handle_apple_collision()
            # self.update()
            self.snake_head.grid(row=self.row, column=self.column, sticky='news')
            self.update()
            last = self.body_objects.pop()
            self.body_objects.insert(0, last)
            self.body_positions.add((self.row, self.column))
            self.body_objects[0].grid(row=old_row, column=old_column)

            self.after(self.refresh_speed, self.movement)
        else:
            ctk.CTkLabel(self, text=f'Game Over, record = {self.snake_tail_length}',
                         font=('helvetica', 30, 'bold')).grid(row=7,
                                                              column=4,
                                                              columnspan=10)

    def game_on(self):
        """
        Checks if the game is still ongoing.

        This method determines whether the game should continue by checking two conditions:
        1. The snake's head is within the bounds of the grid.
        2. The snake's head has not collided with its own body (i.e., it has not hit its tail).

        The grid bounds are defined as rows between 0 and 14 (inclusive) and columns between 0 and 19 (inclusive).
        The method returns `True` if both conditions are met, indicating that the game is still on. Otherwise, it returns `False`.

        :return: bool
            `True` if the game is ongoing, `False` otherwise.
        """
        in_range = 0 <= self.row < 15 and 0 <= self.column < 20
        # print(list(self.body_positions))
        hit_its_tail = (self.row, self.column) in list(self.body_positions)
        return in_range and not hit_its_tail

    def handle_apple_collision(self):
        """
        Checks if the snake's head has collided with the apple.

        This method checks if the current position of the snake's head matches the position of the apple.
        If a collision is detected (i.e., the snake's head is at the same row and column as the apple),
        the following actions are performed:

        1. The snake's tail length is increased by one.
        2. The maximum size of the snake's body list is updated to reflect the new tail length.
        3. The apple is removed from its current position on the grid.
        4. A new random position is generated for the apple.
        5. The speed for the snake's movement is increased by 5 milliseconds.
        6. A debug message is logged with the new position of the apple and the updated tail length of the snake.

        :return: None
        """

        if self.row == self.apple_row and self.column == self.apple_column:
            self.body_objects.append(ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0))
            self.snake_tail_length += 1
            self.body_positions.max_size = self.snake_tail_length

            self.apple.grid_forget()
            self.randomize_apple_position()
            self.refresh_speed -= 5

    def change_direction(self, event=None, direction=None):
        """
        Changes the direction of the snake's movement.

        This method updates the direction in which the snake is moving. It sets the snake's
        direction to the specified `direction` parameter and logs the change for debugging purposes.

        :param event: Optional; the event object associated with the key press. Default is `None`.
        :param direction: str; the new direction for the snake's movement. Expected values are
                          'up', 'down', 'left', or 'right'.
        :return: None
        """
        self.direction = direction


app = Snake()
app.mainloop()
