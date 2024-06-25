import customtkinter as ctk
from settings import *
from random import randint


class Snake(ctk.CTk):
    def __init__(self):
        super().__init__()

        # window setup
        self.title('Snake')
        self.geometry(f'{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}')

        self.grid_window()

        self.direction = 'right'  # starting direction
        self.bind('<Up>', lambda e: self.change_direction(e, 'up'))
        self.bind('<Down>', lambda e: self.change_direction(e, 'down'))
        self.bind('<Left>', lambda e: self.change_direction(e, 'left'))
        self.bind('<Right>', lambda e: self.change_direction(e, 'right'))
        self.generate_random_apple()

        # starting position
        self.row = START_POS[1]
        self.column = START_POS[0]
        self.snake_frm = ctk.CTkFrame(self, fg_color=SNAKE_HEAD_COLOR, corner_radius=0)
        self.snake_frm.grid(row=self.row, column=self.column, sticky='news')
        self.movement()

    def generate_random_apple(self):
        # creating a random apple
        self.frm = ctk.CTkFrame(self, fg_color=APPLE_COLOR)
        self.apple_row = randint(0, 15)
        self.apple_column = randint(0, 20)
        print(self.apple_row, self.apple_column)
        self.frm.grid(row=self.apple_row, column=self.apple_column, sticky='news')

    def grid_window(self):
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

        self.check_for_hit()

        self.snake_frm.grid(row=self.row, column=self.column, sticky='news')
        self.after(REFRESH_SPEED, self.movement)

    def check_for_hit(self):
        if self.row == self.apple_row and self.column == self.apple_column:
            self.frm.grid_forget()
            self.generate_random_apple()

    def change_direction(self, event=None, direction=None):
        self.direction = direction


app = Snake()
app.mainloop()
