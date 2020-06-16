import pygame as pg
import pygame_menu as pg_menu
import random


class SnakeSegment:
    def __init__(self, position):
        self.__size = (20, 20)
        self.body = pg.Rect(position, self.__size)
        self.color = (0, 200, 0)

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.body)

    def move(self, new_position):
        """moves the segment to the given position"""
        self.body = pg.Rect(new_position, self.__size)


class SnakeHead(SnakeSegment):
    def __init__(self, position):
        SnakeSegment.__init__(self, position)
        self.__direction = "NONE"
        self.color = (200, 200, 0)

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__direction = value.upper()

    def move_head(self, direction):
        """moves the head in given direction"""
        self.__direction = direction
        if self.direction == "UP":
            self.body.move_ip(0, -20)
        elif self.direction == "DOWN":
            self.body.move_ip(0, 20)
        elif self.direction == "RIGHT":
            self.body.move_ip(20, 0)
        elif self.direction == "LEFT":
            self.body.move_ip(-20, 0)
        else:
            pass


class Snake:
    def __init__(self, position):
        self.head = SnakeHead(position)
        self.body = []
        self.length = 1
        self.direction = "NONE"

    def move(self):
        if self.length > 1:
            self.body[-1].move(self.head.body.topleft)
            self.body.insert(0, self.body.pop())
        self.head.move_head(self.direction)

    def add_segment(self, position):
        self.body.append(SnakeSegment(position))
        self.length += 1

    def delete_segment(self):
        self.body.pop()
        self.length -= 1

    def draw(self, surface):
        self.head.draw(surface)
        if self.length > 1:
            for segment in self.body:
                segment.draw(surface)

    def reset(self, position):
        self.body.clear()
        self.length = 1
        self.direction = "NONE"
        self.head.move(position)


class Game:
    def __init__(self, screen_width=1280, screen_height=720, fps=60):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fps = fps
        self.is_apple = False
        self.background_color = (0, 0, 0)
        pg.init()
        pg.display.init()
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        pg.display.set_caption("Snake")
        self.clock = pg.time.Clock()
        self.snake = Snake((screen_width/2, screen_height/2))
        self.apple = self.drop_apple()
        self.mainMenu = MainMenu(self.screen_width, self.screen_height, self)
        self.deathMenu = DeathMenu(self.screen_width, self.screen_height, self)
        self.pauseMenu = PauseMenu(self.screen_width, self.screen_height, self)
        self.start_position = (self.screen_width/2, self.screen_height/2)
        self.game_states = {"exit": 0, "menu": 1, "game": 2, "death": 3}
        self.game_state = 1
        random.seed()

    def control(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and self.snake.direction != "DOWN":
                self.snake.direction = "UP"
            if event.key == pg.K_DOWN and self.snake.direction != "UP":
                self.snake.direction = "DOWN"
            if event.key == pg.K_RIGHT and self.snake.direction != "LEFT":
                self.snake.direction = "RIGHT"
            if event.key == pg.K_LEFT and self.snake.direction != "RIGHT":
                self.snake.direction = "LEFT"

    def border_cross(self):
        new_position = list(self.snake.head.body.topleft)
        if self.snake.head.body.right > self.screen_width:
            new_position[0] -= self.screen_width
            self.snake.head.move(new_position)
        elif self.snake.head.body.left < 0:
            new_position[0] += self.screen_width
            self.snake.head.move(new_position)
        elif self.snake.head.body.bottom > self.screen_height:
            new_position[1] -= self.screen_height
            self.snake.head.move(new_position)
        elif self.snake.head.body.top < 0:
            new_position[1] += self.screen_height
            self.snake.head.move(new_position)

    def game_cycle(self):
        self.snake.reset(self.start_position)
        while True:
            self.screen.fill(self.background_color)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game_state = self.game_states["exit"]
                    return
                else:
                    self.control(event)
            self.snake.move()
            if self.collide():
                self.game_state = self.game_states["death"]
                return
            self.eat()
            self.set_len(6)
            if not self.is_apple:
                self.drop_apple()
            else:
                self.apple.draw(self.screen)
            self.border_cross()
            self.snake.draw(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)

    def set_len(self, length):
        if self.snake.direction != "NONE" and self.snake.length < length:
            if self.snake.length == 1:
                self.snake.add_segment(self.snake.head.body.topleft)
            else:
                self.snake.add_segment(self.snake.body[-1].body.topleft)

    def drop_apple(self):
        x = random.randrange(0, self.screen_width - 20, 20)
        y = random.randrange(0, self.screen_height - 20, 20)
        self.apple = Apple((x, y),self.background_color)
        while True:
            snake = [segment.body for segment in self.snake.body]
            snake.append(self.snake.head.body)
            if self.apple.body.collidelist(snake) != -1:
                x = random.randrange(0, self.screen_width - 20, 20)
                y = random.randrange(0, self.screen_height - 20, 20)
                self.apple = Apple((x, y), self.background_color)
            else:
                break
        self.is_apple = True
        return self.apple

    def eat(self):
        if self.snake.head.body.colliderect(self.apple.body):
            if self.snake.length == 1:
                self.snake.add_segment(self.snake.head.body.topleft)
            else:
                self.snake.add_segment(self.snake.body[-1].body.topleft)
            self.drop_apple()

    def menu_cycle(self):
        while self.game_state == self.game_states["menu"]:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.game_state = self.game_states["exit"]
                    return

            self.screen.fill(self.background_color)
            self.mainMenu.display(self.screen, events)
            pg.display.update()
            self.clock.tick(self.fps)

    def collide(self):
        snake_body = [segment.body for segment in self.snake.body]
        if self.snake.head.body.collidelist(snake_body) != -1:
            return True
        else:
            return False

    def try_again(self):
        while self.game_state == self.game_states["death"]:
            self.screen.fill(self.background_color)
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.game_state = self.game_states["exit"]
                    return
            self.deathMenu.display(self.screen, events)
            pg.display.update()
            self.clock.tick(self.fps)

    def main_cycle(self):
        while True:
            if self.game_state == self.game_states["menu"]:
                self.menu_cycle()
            elif self.game_state == self.game_states["game"]:
                self.game_cycle()
            elif self.game_state == self.game_states["death"]:
                self.try_again()
            elif self.game_state == self.game_states["exit"]:
                break
            else:
                raise StateError("Unexpected game state")

    def set_difficulty(self, difficulty, fps):
        self.fps = fps

    def start_game(self):
        self.game_state = self.game_states["game"]
        self.game_cycle()


class Apple:
    def __init__(self, position, bg_color):
        self.size = (20, 20)
        self.color = bg_color
        self.position = position
        self.body = pg.Rect(self.position, self.size)
        self.image = pg.image.load("apple_icon.bmp")
        self.image = self.image.convert()
        self.image = pg.transform.scale(self.image, (22, 22))
        self.image.set_colorkey((255, 255, 255))

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.body)
        surface.blit(self.image, self.position)


class StateError(Exception):
    pass


class Menu:
    def __init__(self, width, height, title, background_color):
        self.theme = pg_menu.themes.THEME_DARK.copy()
        self.theme.background_color = background_color
        self.theme.title_background_color = background_color
        self.theme.widget_font_color = (255, 255, 255, 150)
        self.body = pg_menu.menu.Menu(width=width, height=height, title=title, theme=self.theme)

    def display(self, screen, events):
        if self.body.is_enabled():
            self.body.update(events)
            self.body.draw(screen)


class MainMenu(Menu):
    def __init__(self, width, height, game):
        Menu.__init__(self, width, height, "", (0, 0, 0))
        self.body.add_image("snake_menu_img.png", scale=(1.2, 0.9))
        self.body.add_button("Play", game.start_game)
        self.body.add_selector("Difficulty", [("Easy", 15),
                                              ("Normal", 20),
                                              ("Hard", 30),
                                              ("Insane", 45)],
                               onchange=game.set_difficulty)
        self.body.add_button("Exit", pg_menu.events.EXIT)


class PauseMenu(Menu):
    def __init__(self, width, height, game):
        Menu.__init__(self, width, height, title="Pause", background_color=(0, 0, 0, 100))
        self.body.add_button("Resume", pg_menu.events.CLOSE)
        self.body.add_button("Go to menu", self.to_menu, game)

    @staticmethod
    def to_menu(game):
        game.game_state = game.game_states["menu"]


class DeathMenu(Menu):
    def __init__(self, width, height, game):
        Menu.__init__(self, width, height, title="", background_color=(0, 0, 0, 100))
        self.body.add_label("YOU'RE DEAD", font_size=40)
        self.body.add_vertical_margin(150)
        self.body.add_button("Try again", self.try_again, game, )
        self.body.add_button("Go to menu", self.to_menu, game)

    @staticmethod
    def try_again(game):
        game.game_state = game.game_states["game"]
        game.snake.reset(game.start_position)

    @staticmethod
    def to_menu(game):
        game.game_state = game.game_states["menu"]
