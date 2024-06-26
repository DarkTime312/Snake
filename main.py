import customtkinter as ctk
from settings import *
from random import randint
from util import LimitedList


class Snake(ctk.CTk):
    """
    A class representing the Snake game using CustomTkinter.
    """

    def __init__(self):
        """
        Initialize the Snake game window and start the game.

        This method sets up the main game window, configures the grid layout,
        and starts the initial game state.
        """
        super().__init__()

        # window setup
        self.title('Snake')
        self.geometry(f'{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}')
        # Configure the grid layout for the window
        self.grid_window()
        # Set up keyboard controls
        self.bind_keyboard()
        # Initialize the starting state of the game
        self.start_game()

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

    def start_game(self):
        """
        Initialize or reset the game state to start a new game.

        This method performs the following actions:
        1. Clears all existing widgets from the window.
        2. Sets the initial direction of the snake.
        3. Creates and positions the apple.
        4. Sets initial game parameters (speed, snake length).
        5. Creates the snake's head and body parts.
        6. Positions the snake on the grid.
        7. Starts the snake's movement.

        This method can be called to start a new game or to reset the game after it ends.
        """
        # Clear all existing widgets from the window
        for widget in self.winfo_children():
            widget.destroy()

        # Set the initial direction of the snake
        self.direction = 'right'

        # Create the apple and place it randomly on the grid
        self.apple = ctk.CTkFrame(self, fg_color=APPLE_COLOR)
        self.randomize_apple_position()

        # Set initial game parameters
        self.refresh_speed = 250  # Movement speed of the snake
        self.snake_body_length = 3  # Initial length of the snake

        # Initialize the starting position of the snake's head
        self.row = START_POS[1]
        self.column = START_POS[0]

        # Create a limited list to store the snake's body parts
        self.body_positions = LimitedList(3)  # Stores positions of body parts
        self.body_objects = []  # Stores the actual body part widgets

        # Create the snake's head
        self.snake_head = ctk.CTkFrame(self, fg_color=SNAKE_HEAD_COLOR, corner_radius=0)

        # Create and add initial body parts to the snake's body list
        self.create_body_parts(number=2)

        self.initialize_snake_position()

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

        :return: None
        """

        # Calculate the maximum possible row and column indices
        # Subtract 1 from FIELDS dimensions to account for 0-based indexing
        max_row_index = FIELDS[1] - 1
        max_column_index = FIELDS[0] - 1

        # Generate random row and column indices for the apple
        self.apple_row = randint(0, max_row_index)
        self.apple_column = randint(0, max_column_index)

        # Place the apple at the randomly generated position on the grid
        # The 'grid' method is used to position the apple widget
        self.apple.grid(row=self.apple_row, column=self.apple_column)

    def initialize_snake_position(self):
        """
        Initialize the starting position of the snake on the grid.

        This method sets up the initial body positions of the snake,
        places the body parts on the grid, and positions the snake's head.
        """

        # Add initial body positions
        self.body_positions.add((self.row, self.column - 2))
        self.body_positions.add((self.row, self.column - 1))
        self.body_positions.add((self.row, self.column))

        # Place body parts on the grid
        for body_part, (row, column) in zip(self.body_objects, self.body_positions):
            body_part.grid(row=row, column=column, sticky='news')

        # Place the snake's head on the grid
        self.snake_head.grid(row=self.row, column=self.column)

    def movement(self):
        """
        Handles the movement of the snake in the game.

        This method updates the snake's position based on the current direction,
        checks for collisions, updates the snake's body, and manages the game flow.

        The method performs the following steps:
        1. Updates the snake's head position based on the current direction.
        2. Checks if the game can continue.
        3. If the game can continue:
           - Handles potential apple collisions.
           - Updates the position of the snake's head on the grid.
           - Updates the snake's body parts.
           - Schedules the next movement.
        4. If the game cannot continue, it triggers the game over sequence.

        The movement is recursive, scheduling itself to run again after a delay
        defined by self.refresh_speed, creating the continuous movement of the snake.
        """

        # Store the current direction and the old position of the snake's head
        current_direction = self.direction
        old_row = self.row
        old_column = self.column

        # Update the snake's head position based on the current direction
        # DIRECTIONS is a dictionary mapping directions to coordinate changes
        self.row += DIRECTIONS.get(current_direction)[1]
        self.column += DIRECTIONS.get(current_direction)[0]

        # Check if the game can continue (e.g., no collisions with walls or self)
        if self.can_game_continue():
            # Check and handle if the snake has collided with an apple
            self.handle_apple_collision()

            # Update the position of the snake's head on the grid
            self.snake_head.grid(row=self.row, column=self.column, sticky='news')

            # Update the positions of the snake's body parts
            self.update_body_positions(cur_row=self.row,
                                       cur_col=self.column,
                                       old_row=old_row,
                                       old_col=old_column)

            # Schedule the next movement after a delay (self.refresh_speed)
            self.after(self.refresh_speed, self.movement)
        else:
            # If the game cannot continue, trigger the game over sequence
            self.game_over()

    def update_body_positions(self, cur_row, cur_col, old_row, old_col):
        """
        Updates the position of the snake's body parts.

        This method is responsible for moving the snake's body parts to follow
        the head's movement. It updates both the visual representation and the
        internal data structures tracking the snake's body.

        Args:
        cur_row (int): The current row of the snake's head.
        cur_col (int): The current column of the snake's head.
        old_row (int): The previous row of the snake's head.
        old_col (int): The previous column of the snake's head.

        The method performs the following operations:
        1. Removes the last body part from the list of body objects.
        2. Inserts this part at the beginning of the list (just behind the head).
        3. Adds the current head position to the body positions.
        4. Updates the grid position of the new first body part to the old head position.

        This creates the effect of the snake's body following its head as it moves.
        """

        last = self.body_objects.pop()
        self.body_objects.insert(0, last)
        self.body_positions.add((cur_row, cur_col))
        self.body_objects[0].grid(row=old_row, column=old_col)

    def game_over(self):
        """
        Handles the game over state and displays the end game screen.

        This method is called when the game ends, typically when the snake collides
        with itself or the game boundaries. It performs the following actions:

        1. Displays a "Game Over" message along with the player's score (snake length).
           The message is shown as a CTkLabel widget centered on the screen.

        2. Creates a "Play Again" button that allows the player to restart the game.
           The button is positioned below the game over message and is linked to
           the start_game method.
        """
        ctk.CTkLabel(self,
                     text=f'Game Over, record = {self.snake_body_length}',
                     font=('helvetica', 30, 'bold')).place(relx=0.5, rely=0.5, anchor='center')
        ctk.CTkButton(self,
                      text='Play Again!',
                      command=self.start_game,
                      text_color='black',
                      font=('B Titr', 25, 'bold')
                      ).place(relx=0.5, rely=0.6, anchor='center')

    def can_game_continue(self):
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

        :return: None
        """

        if self.row == self.apple_row and self.column == self.apple_column:
            self.snake_body_length += 1
            self.body_positions.max_size = self.snake_body_length
            self.create_body_parts(number=1)

            self.apple.grid_forget()
            self.randomize_apple_position()
            self.refresh_speed -= 5

    def change_direction(self, event=None, direction=None):
        """
        Changes the direction of the snake's movement.

        This method updates the direction in which the snake is moving. It sets the snake's
        direction to the specified `direction` parameter.

        :param event: Optional; the event object associated with the key press. Default is `None`.
        :param direction: str; the new direction for the snake's movement. Expected values are
                          'up', 'down', 'left', or 'right'.
        :return: None
        """
        self.direction = direction

    def create_body_parts(self, number: int = 1):
        """
        Creates and adds new body parts to the snake.

        This method generates new body segments for the snake and adds them to the
        internal list of body objects. Each body part is represented by a CTkFrame
        widget with specific visual properties.

        Args:
            number (int, optional): The number of body parts to create. Defaults to 1.

        The method performs the following actions:
        1. Iterates 'number' times to create the specified number of body parts.
        2. For each iteration, it creates a new CTkFrame widget with the following properties:
           - Parent widget: self (the current instance)
           - Foreground color: Defined by SNAKE_BODY_COLOR constant
           - Corner radius: 0 (creating a square shape)
        3. Appends each new body part to the self.body_objects list.

        Note:
        - The created body parts are not immediately placed on the game grid.
          Their positioning will be handled separately.

        This method is typically called when the snake grows after eating an apple
        or during the initial setup of the game.
        """
        for _ in range(number):
            body_part = ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)
            self.body_objects.append(body_part)


app = Snake()
app.mainloop()
