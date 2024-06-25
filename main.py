import customtkinter as ctk
from settings import *
from random import randint
import logging
from util import LimitedList

# logging.disable()
# Set up logging
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s - %(message)s')


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
        self.snake_tail_length = 2

        # Initialize the starting position of the snake's head
        self.row = START_POS[1]
        self.column = START_POS[0]
        # Create a limited list to store the snake's body parts
        self.body_list = LimitedList(2)

        # Create the snake's head frame and place it on the grid
        self.snake_head = ctk.CTkFrame(self, fg_color=SNAKE_HEAD_COLOR, corner_radius=0)
        self.snake_head.grid(row=self.row, column=self.column)

        # Add initial body parts to the snake's body list
        self.body_list.add((self.row, self.column - 2, ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)))
        self.body_list.add((self.row, self.column - 1, ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)))

        # Log the initial positions of the snake's body parts
        logging.debug("Initial body parts:")
        for row, column, body_part in self.body_list:
            logging.debug(f"Body part at row {row}, column {column}")
            body_part.grid(row=row, column=column)

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
        # Log apple position
        logging.debug(f"Apple generated at row {self.apple_row}, column {self.apple_column}")

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
        current_direction = self.direction

        self.row += DIRECTIONS.get(current_direction)[1]
        self.column += DIRECTIONS.get(current_direction)[0]
        if self.game_on():
            self.handle_apple_collision()
            # self.update()
            for row, column, body_part in self.body_list:
                logging.debug(f"Body part at row {row}, column {column}")
                body_part.grid(row=row, column=column)
            logging.debug(f"Snake head at row {self.row}, column {self.column}")
            self.snake_head.grid(row=self.row, column=self.column, sticky='news')

            # Remove the tail part from the grid
            tail_row, tail_column, tail_part = self.body_list[0]
            tail_part.grid_forget()
            # Add new head position to the body list
            new_body_part = ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)
            self.body_list.add((self.row, self.column, new_body_part))
            # Log body parts after movement
            logging.debug("Body parts after movement:")
            for row, column, body_part in self.body_list:
                logging.debug(f"Body part at row {row}, column {column}")

            self.after(self.refresh_speed, self.movement)
        else:
            ctk.CTkLabel(self, text=f'Game Over, record = {self.snake_tail_length}',
                         font=('helvetica', 30, 'bold')).grid(row=7,
                                                              column=4,
                                                              columnspan=10)
            logging.debug(f"Game Over, record = {self.snake_tail_length}")

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
        hit_its_tail = (self.row, self.column) in [(row, column) for row, column, _ in self.body_list]
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
            self.snake_tail_length += 1
            self.body_list.max_size = self.snake_tail_length

            self.apple.grid_forget()
            self.randomize_apple_position()
            self.refresh_speed -= 5
            logging.debug(
                f"Apple hit at row {self.apple_row}, column {self.apple_column}. New length: {self.snake_tail_length}")

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
        logging.debug(f"Direction changed to {self.direction}")


app = Snake()
app.mainloop()
