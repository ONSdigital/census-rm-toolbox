import curses
import functools
import itertools
import time
from collections import deque
from contextlib import contextmanager, suppress

WIDTH = 80
HEIGHT = 40


class Game:

    def __init__(self):
        self.snake = Snake(zip(10 * [10], range(10, 0, -1)), (0, 1))  # TODO intelligent randomise
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

    def draw_snake(self):
        for coord in self.snake.coords:
            self.game_window.addch(coord[0], coord[1], self.snake.display_char)

    def draw_game(self):
        self.game_window.clear()
        with suppress(curses.error):
            self.draw_snake()
            self.game_window.border()

        self.game_window.refresh()

    def begin_game(self):
        while True:
            with self.wait_for_full_frame_time():
                self.render_frame()
                if self.is_lost():
                    self.lost = True
                    break

    def is_lost(self):
        return self.snake.is_outside_bound() or self.snake.head_hit_tail()

    def handle_keys(self):
        key = self.screen.getch()
        self.key_map.get(key, lambda: None)()

    def render_frame(self):
        self.draw_game()
        self.handle_keys()
        self.snake.update()
        self.frame_count += 1

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
            self.any_key_to_continue('PRESS ANY KEY TO START')
            self.begin_game()
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

    def any_key_to_continue(self, message):
        self.screen.refresh()
        splash_window = curses.newwin(30, 60, 10, 10)
        splash_window.addstr(10, 15, message)
        splash_window.border()
        splash_window.touchwin()
        splash_window.refresh()
        while True:
            if self.screen.getch() not in {-1, 10}:
                break
        del splash_window
        self.screen.refresh()


class Snake:
    display_char = '#'

    def __init__(self, initial_coords, direction):
        self.coords = deque()
        for coord in initial_coords:
            self.coords.append(coord)

        self.direction = direction
        self.speed = 1

    def change_direction(self, new_direction):
        # Can't reverse direction
        if abs(self.direction[0] - new_direction[0]) <= 1 and abs(self.direction[1] - new_direction[1]) <= 1:
            self.direction = new_direction

    def update(self):
        self.coords.pop()
        self.coords.appendleft((self.coords[0][0] + (self.direction[0] * self.speed),
                                self.coords[0][1] + (self.direction[1] * self.speed)))

    def is_outside_bound(self):
        return (any(HEIGHT <= coord[0] or coord[0] <= 0 for coord in self.coords)
                or any(WIDTH <= coord[1] or coord[1] <= 0 for coord in self.coords))

    def head_hit_tail(self):
        return any(self.coords[0] == tail_coord for tail_coord in itertools.islice(self.coords, 1, len(self.coords)))


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
