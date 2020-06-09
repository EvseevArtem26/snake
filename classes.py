import pygame as pg
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
        self.game_over = False
        self.quit = False
        self.is_apple = False
        self.background_color = (0, 0, 0)
        pg.init()
        pg.display.init()
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        pg.display.set_caption("Snake")
        self.clock = pg.time.Clock()
        self.snake = Snake((screen_width/2, screen_height/2))
        self.apple = self.drop_apple()
        self.start_position = (self.screen_width/2, self.screen_height/2)
        self.font = pg.font.SysFont("Arial", 36)
        self.menu_text = self.font.render("Press enter to start", False, (255, 255, 255))
        random.seed()

    def get_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
            elif event.type == pg.KEYDOWN:
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

    def main_cycle(self):
        while not self.quit:
            self.screen.fill(self.background_color)
            self.get_event()
            self.snake.move()
            self.collide()
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
        self.apple = Apple((x, y))
        while True:
            snake = [segment.body for segment in self.snake.body]
            snake.append(self.snake.head.body)
            if self.apple.body.collidelist(snake) != -1:
                x = random.randrange(0, self.screen_width - 20, 20)
                y = random.randrange(0, self.screen_height - 20, 20)
                self.apple = Apple((x, y))
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

    def menu(self):
        self.screen.fill(self.background_color)
        pass

    def collide(self):
        snake_body = [segment.body for segment in self.snake.body]
        if self.snake.head.body.collidelist(snake_body) != -1:
            self.snake.reset(self.start_position)


class Apple():
    def __init__(self, position):
        self.size = (20, 20)
        self.color = (230, 0, 0)
        self.body = pg.Rect(position, self.size)

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.body)
