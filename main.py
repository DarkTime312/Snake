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
        self.apple = ctk.CTkFrame(self, fg_color=APPLE_COLOR)

        self.grid_window()

        self.direction = 'right'  # starting direction
        self.bind('<Up>', lambda e: self.change_direction(e, 'up'))
        self.bind('<Down>', lambda e: self.change_direction(e, 'down'))
        self.bind('<Left>', lambda e: self.change_direction(e, 'left'))
        self.bind('<Right>', lambda e: self.change_direction(e, 'right'))
        self.generate_random_apple()
        self.refresh_speed = 250

        # starting position
        self.row = START_POS[1]
        self.column = START_POS[0]
        self.body_list = LimitedList(2)

        self.snake_head = ctk.CTkFrame(self, fg_color=SNAKE_HEAD_COLOR, corner_radius=0)
        self.snake_head.grid(row=self.row, column=self.column)

        self.body_list.add((self.row, self.column - 2, ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)))
        self.body_list.add((self.row, self.column - 1, ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)))

        self.snake_length = 2

        for row, column, body_part in self.body_list:
            body_part.grid(row=row, column=column)

        self.movement()

    def generate_random_apple(self):
        # creating a random apple
        max_row_index = FIELDS[1] - 1
        max_column_index = FIELDS[0] - 1

        self.apple_row = randint(0, max_row_index)
        self.apple_column = randint(0, max_column_index)
        self.apple.grid(row=self.apple_row, column=self.apple_column)

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
        if self.game_on():
            self.check_for_hit()
            # self.update()
            for row, column, body_part in self.body_list:
                print(f"{row=}, {column=}")
                body_part.grid(row=row, column=column)
            print(f"{self.row=}, {self.column=}")
            self.snake_head.grid(row=self.row, column=self.column, sticky='news')

            # Remove the tail part from the grid
            tail_row, tail_column, tail_part = self.body_list[0]
            tail_part.grid_forget()
            # Add new head position to the body list
            new_body_part = ctk.CTkFrame(self, fg_color=SNAKE_BODY_COLOR, corner_radius=0)
            self.body_list.add((self.row, self.column, new_body_part))

            self.after(self.refresh_speed, self.movement)
        else:
            ctk.CTkLabel(self, text=f'Game Over, record = {self.snake_length}', font=('helvetica', 30, 'bold')).grid(row=7,
                                                                                                                     column=5,
                                                                                                                     columnspan=8)

    def game_on(self):
        in_range = 0 <= self.row < 15 and 0 <= self.column < 20
        hit_its_tail = (self.row, self.column) in [(row, column) for row, column, _ in self.body_list]
        return in_range and not hit_its_tail

    def check_for_hit(self):
        if self.row == self.apple_row and self.column == self.apple_column:
            self.snake_length += 1
            self.body_list.max_size = self.snake_length

            self.apple.grid_forget()
            self.generate_random_apple()
            self.refresh_speed -= 5
        # print(list(self.body_list))

    def change_direction(self, event=None, direction=None):
        self.direction = direction


app = Snake()
app.mainloop()
