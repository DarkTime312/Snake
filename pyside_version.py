import sys
from random import randint

from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QPalette, QColor, Qt, QFont, QIcon
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QGridLayout, QLabel, QStackedLayout, QVBoxLayout, \
    QPushButton
from hPyT import *

from settings import *
from util import LimitedList


class Board(QWidget):
    def __init__(self):
        super().__init__()
        self.set_background_color("#242424")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setup_layout()
        self.start_game()

    def set_background_color(self, color: str):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # Important to enable background color

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
        # Clear all existing snake parts from the window
        for widget in self.findChildren(QLabel):
            if widget.objectName() != 'score_lbl':
                widget.deleteLater()

        self.stacked_layout.setCurrentIndex(0)

        # Set the initial direction of the snake
        self.direction = 'right'

        # Create the apple and place it randomly on the grid
        self.apple = self.create_object(APPLE_COLOR, apple=True)

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
        self.snake_head = self.create_object(SNAKE_HEAD_COLOR)

        # Create and add initial body parts to the snake's body list
        self.create_body_parts(number=2)

        self.initialize_snake_position()

        self.timer = QTimer()
        self.timer.setInterval(REFRESH_SPEED)
        self.timer.timeout.connect(self.movement)

        # Start the snake's movement
        self.timer.start()

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
            self.grid_layout.addWidget(self.snake_head, self.row, self.column)

            # Update the positions of the snake's body parts
            self.update_body_positions(cur_row=self.row,
                                       cur_col=self.column,
                                       old_row=old_row,
                                       old_col=old_column)

        else:
            # If the game cannot continue, trigger the game over sequence
            self.game_over()

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
        self.lbl_score.setText(f'Game Over, record = {self.snake_body_length}')
        self.stacked_layout.setCurrentIndex(1)

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
        self.grid_layout.addWidget(self.body_objects[0], old_row, old_col)

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

            self.grid_layout.removeWidget(self.apple)

            self.randomize_apple_position()
            self.refresh_speed -= 5
            self.timer.setInterval(self.refresh_speed)

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
        in_range = (TOP_LIMIT <= self.row < BOTTOM_LIMIT) and (LEFT_LIMIT <= self.column < RIGHT_LIMIT)
        hit_its_tail = (self.row, self.column) in list(self.body_positions)
        return in_range and not hit_its_tail

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
            self.grid_layout.addWidget(body_part, row, column)

        # Place the snake's head on the grid
        self.grid_layout.addWidget(self.snake_head, self.row, self.column)

    def create_object(self, color: str, apple=False) -> QLabel:
        border_radius = 5 if apple else 0
        body_part = QLabel()
        body_part.setStyleSheet(f"background-color: {color}; border: 2px solid transparent; border-radius:{border_radius}px")
        return body_part

    def change_direction(self, direction=None):
        """
        Change the direction of the snake's movement.

        This method updates the snake's direction based on the input, ensuring that
        the snake cannot immediately reverse its direction. The new direction is only
        applied if it's not directly opposite to the current direction.

        Parameters:
        event (tkinter.Event, optional): The event that triggered the direction change.
                                         This parameter is not used in the method but is
                                         included for compatibility with event bindings.
        direction (str): The new direction to change to. Must be one of 'up', 'down', 'left', or 'right'.

        Rules for direction change:
        - If moving right, cannot change to left
        - If moving left, cannot change to right
        - If moving up, cannot change to down
        - If moving down, cannot change to up

        The method silently ignores invalid direction changes (i.e., trying to reverse direction).

        Returns:
        None
        """
        if self.direction == 'right' and direction != 'left':
            self.direction = direction
        elif self.direction == 'left' and direction != 'right':
            self.direction = direction
        elif self.direction == 'up' and direction != 'down':
            self.direction = direction
        elif self.direction == 'down' and direction != 'up':
            self.direction = direction

    def keyPressEvent(self, event):
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
        if event.key() == Qt.Key.Key_Up:
            self.change_direction('up')
        elif event.key() == Qt.Key.Key_Down:
            self.change_direction('down')
        elif event.key() == Qt.Key.Key_Right:
            self.change_direction('right')
        elif event.key() == Qt.Key.Key_Left:
            self.change_direction('left')

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
        self.grid_layout.addWidget(self.apple, self.apple_row, self.apple_column)

    def setup_layout(self):
        """
        Configures the grid layout for the window.

        This method sets up the grid layout for the window by configuring the rows and columns
        based on the number of rows and columns specified in the `FIELDS` constant. Each row and
        column is configured to have an equal weight and uniform size, ensuring that the grid
        cells are evenly distributed across the window.

        :return: None
        """

        self.stacked_layout = QStackedLayout()
        first_layout_widget = QWidget()
        second_layout_widget = QWidget()

        self.stacked_layout.addWidget(first_layout_widget)
        self.stacked_layout.addWidget(second_layout_widget)
        self.setLayout(self.stacked_layout)

        # Create additional layouts
        self.grid_layout = QGridLayout()
        second_layout = QVBoxLayout()

        first_layout_widget.setLayout(self.grid_layout)
        second_layout_widget.setLayout(second_layout)

        # set up the grid layout
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)

        number_of_rows = FIELDS[1]
        number_of_columns = FIELDS[0]

        # creating the rows
        for row in range(number_of_rows):
            self.grid_layout.setRowStretch(row, 1)  # Set equal stretch factor

        # creating the columns
        for col in range(number_of_columns):
            self.grid_layout.setColumnStretch(col, 1)  # Set equal stretch factor

        # Create game over window widgets
        self.lbl_score = QLabel()
        self.lbl_score.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.lbl_score.setObjectName('score_lbl')
        self.lbl_score.setStyleSheet("color: white")
        self.lbl_score.setFont(QFont('helvetica', 30, QFont.Weight.Bold))

        btn_play_again = QPushButton('Play again?')
        btn_play_again.setFont(QFont('helvetica', 30, QFont.Weight.Bold))
        btn_play_again.setFixedSize(250, 100)
        btn_play_again.clicked.connect(self.start_game)
        # Add these widgets to the layout
        second_layout.addStretch()
        second_layout.addWidget(self.lbl_score)
        second_layout.addWidget(btn_play_again, alignment=Qt.AlignmentFlag.AlignCenter)
        second_layout.addStretch()

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
            body_part = self.create_object(SNAKE_BODY_COLOR)
            self.body_objects.append(body_part)


class SnakeGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(QSize(WINDOW_SIZE[0], WINDOW_SIZE[1]))
        self.setWindowTitle('Snake Game')
        self.set_titlebar_color()
        self.setWindowIcon(QIcon('empty.ico'))

        self.board = Board()
        self.setCentralWidget(self.board)

    def set_titlebar_color(self):
        title_bar_color.set(self, '#000000')  # sets the titlebar color to white


app = QApplication(sys.argv)
window = SnakeGame()
window.show()
app.exec()
