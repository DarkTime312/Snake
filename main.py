import customtkinter as ctk
from settings import *
from random import randint

from collections import deque


class LimitedList:
    def __init__(self, max_size):
        self._max_size = max_size
        self.items = deque(maxlen=max_size)

    @property
    def max_size(self):
        return self._max_size

    @max_size.setter
    def max_size(self, new_max_size):
        if new_max_size < len(self.items):
            # If new size is smaller, remove excess items from the left
            while len(self.items) > new_max_size:
                self.items.popleft()
        self._max_size = new_max_size
        self.items = deque(self.items, maxlen=new_max_size)

    def add(self, item):
        self.items.append(item)

    def get_all(self):
        return list(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def __iter__(self):
        return iter(self.items)


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
        self.body_list = LimitedList(2)

        self.snake_head = ctk.CTkFrame(self, fg_color=SNAKE_HEAD_COLOR, corner_radius=0)
        self.snake_head.grid(row=self.row, column=self.column)

        self.body_list.add((self.row, self.column - 1, ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)))
        self.body_list.add((self.row, self.column - 2, ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)))

        self.length = 2

        for row, column, body_part in self.body_list:
            body_part.grid(row=row, column=column)

        self.movement()

    def generate_random_apple(self):
        # creating a random apple
        self.frm = ctk.CTkFrame(self, fg_color=APPLE_COLOR)
        self.apple_row = randint(0, FIELDS[1] - 1)
        self.apple_column = randint(0, FIELDS[0] - 1)
        # print(self.apple_row, self.apple_column)
        self.frm.grid(row=self.apple_row, column=self.apple_column)

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
        if 0 <= self.row < 15 and 0 <= self.column < 20:

            self.check_for_hit()
            self.snake_head.grid(row=self.row, column=self.column, sticky='news')
            for row, column, body_part in self.body_list:
                body_part.grid(row=row, column=column)

            self.after(REFRESH_SPEED, self.movement)
        else:
            print('game over')

    def check_for_hit(self):
        if self.row == self.apple_row and self.column == self.apple_column:
            self.length += 1
            self.body_list.max_size = self.length

            # print(self.length)
            self.frm.grid_forget()
            self.generate_random_apple()
        print(self.body_list[0][2])
        self.body_list[0][2].grid_forget()
        self.body_list.add((self.row, self.column, ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)))

    def change_direction(self, event=None, direction=None):
        self.direction = direction


app = Snake()
app.mainloop()
