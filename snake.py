import curses
import functools
import itertools
import random
import time
from collections import deque
from contextlib import contextmanager, suppress

WIDTH = 60
HEIGHT = 30


class Game:

    def __init__(self):
        self.board = set(tuple([y, x]) for x in range(1, WIDTH) for y in range(1, HEIGHT))
        self.snake = Snake(zip(10 * [10], range(10, 0, -1)), (0, 1))  # TODO intelligent randomise
        self.food = None
        self.spawn_food()
        self.score = 0
        self.screen = None
        self.game_window = None
        self.lost = False
        self.key_map = {
            ord('w'): functools.partial(self.snake.change_direction, (-1, 0)),
            ord('s'): functools.partial(self.snake.change_direction, (1, 0)),
            ord('a'): functools.partial(self.snake.change_direction, (0, -1)),
            ord('d'): functools.partial(self.snake.change_direction, (0, 1)),
        }
        self.frame_count = 0
        self.game_speed = 6  # in movements per second

        self.DEBUG = None

    def spawn_food(self):
        possible_coords = self.board.difference(self.snake.coords)
        self.food = Food(random.choice(list(possible_coords)))

    def handle_scoring(self):
        if self.eating_food():
            self.score += 1
            self.game_speed += 1
            self.snake.grow()
            self.spawn_food()

    def draw_snake(self):
        self.game_window.addch(self.snake.get_head()[0], self.snake.get_head()[1], self.snake.head_char)
        for tail_coord in self.snake.get_tail():
            self.game_window.addch(tail_coord[0], tail_coord[1], self.snake.tail_char)

    def draw_food(self):
        self.game_window.addch(self.food.coords[0], self.food.coords[1], self.food.display_char)

    def draw_game(self):
        self.game_window.clear()
        with suppress(curses.error):
            self.draw_snake()
            self.draw_food()
            self.game_window.border()

        self.game_window.refresh()

    def begin_game(self):
        while True:
            with self.wait_for_full_frame_time():
                self.render_frame()
                if self.lost:
                    break

    def run_game_loop(self):

    def is_lost(self):
        return self.snake.is_outside_bound() or self.snake.head_hit_tail()

    def handle_loss(self):
        if self.is_lost():
            self.lost = True

    def handle_keys(self):
        key = self.screen.getch()
        self.key_map.get(key, lambda: None)()

    def render_frame(self):
        self.draw_game()
        self.handle_scoring()
        self.handle_loss()
        self.handle_keys()
        self.snake.update()
        self.frame_count += 1

    def eating_food(self):
        return self.snake.get_head() == self.food.coords

    @contextmanager
    def wait_for_full_frame_time(self, ):
        frame_start = time.time()
        yield
        frame_time = time.time() - frame_start
        if frame_time < (1 / self.game_speed):
            time.sleep(1 / self.game_speed - frame_time)

    def start(self):
        try:
            self.configure_curses()
            self.key_to_continue_splash('   PRESS A [S] KEY TO START\n\n'
                                        '   WASD to move, CTRL+C to exit', continue_keys={ord('s')})
            self.begin_game()
            self.key_to_continue_splash(f'GAME OVER, SCORE: {self.score}\n\n'
                                        f'      [Q] TO EXIT', continue_keys={ord('q')})
        finally:
            curses.endwin()

    def configure_curses(self):
        with suppress(curses.error):
            self.screen = curses.initscr()
            self.screen.nodelay(True)
            self.screen.keypad(False)
            self.game_window = curses.newwin(HEIGHT, WIDTH, 1, 1)
            curses.nocbreak()
            curses.noecho()
            curses.curs_set(0)

    def key_to_continue_splash(self, message, continue_keys=None):
        message_lines = message.split('\n')
        splash_height = len(message_lines) + 2
        splash_width = max(len(line) for line in message_lines) + 4
        self.screen.refresh()
        splash_window = curses.newwin(splash_height, splash_width, (HEIGHT - splash_height) // 2, (WIDTH - splash_width) // 2)
        splash_window.addstr(1, 2, message)
        splash_window.border()
        splash_window.touchwin()
        splash_window.refresh()
        while True:
            # TODO fix whatever is going on here
            if (continue_keys and self.screen.getch() in continue_keys
                    or not continue_keys and self.screen.getch() not in {-1, 10}):
                break
        del splash_window
        self.screen.refresh()


class Snake:
    tail_char = '#'
    head_char = '#'

    def __init__(self, initial_coords, direction):
        self.coords = deque()
        for coord in initial_coords:
            self.coords.append(coord)

        self.direction = direction
        self.speed = 1
        self.last_tail = self.coords[-1]

    def change_direction(self, new_direction):
        # Can't reverse direction
        if abs(self.direction[0] - new_direction[0]) <= 1 and abs(self.direction[1] - new_direction[1]) <= 1:
            self.direction = new_direction

    def update(self):
        self.last_tail = self.coords.pop()
        self.coords.appendleft((self.coords[0][0] + (self.direction[0] * self.speed),
                                self.coords[0][1] + (self.direction[1] * self.speed)))

    def is_outside_bound(self):
        return (any(HEIGHT - 1 <= coord[0] or coord[0] <= 0 for coord in self.coords)
                or any(WIDTH - 1 <= coord[1] or coord[1] <= 0 for coord in self.coords))

    def head_hit_tail(self):
        return any(self.get_head() == tail_coord for tail_coord in self.get_tail())

    def get_head(self):
        return self.coords[0]

    def get_tail(self):
        return itertools.islice(self.coords, 1, len(self.coords))

    def grow(self):
        self.coords.append(self.last_tail)


class Food:
    display_char = 'x'

    def __init__(self, coords):
        self.coords = coords


if __name__ == '__main__':
    try:
        game = Game()
        game.start()
        if game.lost:
            print('GAME OVER')
    except KeyboardInterrupt:
        print('EXIT BY KEYBOARD')
    finally:
        # Belt and braces
        if not curses.isendwin():
            curses.endwin()
