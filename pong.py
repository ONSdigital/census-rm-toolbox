import curses
import time

from pynput import keyboard


class Game:
    WIDTH = 80
    HEIGHT = 40

    def __init__(self):
        self.grid = self.HEIGHT * [self.WIDTH * [' ']]
        self.ball = [10, 10]

        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        curses.nocbreak()
        curses.noecho()
        self.screen = curses.initscr()

    def update_point(self, x, y, value):
        self.grid[y][x] = value

    def draw(self):
        try:
            self.screen.addstr('\n'.join(''.join(row) for row in self.grid))
        except curses.error:
            pass
        self.screen.refresh()

    def move_ball(self, x_shift, y_shift):
        self.update_point(self.ball[0], self.ball[1], ' ')
        self.ball[0] = (self.ball[0] + x_shift) % self.WIDTH
        self.ball[1] = (self.ball[1] + y_shift) % self.HEIGHT
        self.update_point(self.ball[0], self.ball[1], 'o')

    def on_press(self, key):
        actions = {
            keyboard.Key.up: self.move_ball(0, 1),
            keyboard.Key.down: self.move_ball(0, -1),
            keyboard.Key.left: self.move_ball(-1, 0),
            keyboard.Key.right: self.move_ball(1, 0),
        }
        actions.get(key, lambda: None)()

    def start(self):
        self.keyboard_listener.start()
        while True:
            frame_start = time.time()
            self.draw()
            frame_time = time.time() - frame_start
            if frame_time < (1 / 60):
                time.sleep(1 / 60 - frame_time)

    def end(self):
        curses.endwin()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()

    def __enter__(self):
        return self


if __name__ == '__main__':

    with Game() as game:
        game.start()
