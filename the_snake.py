from random import randint

import pygame
from pygame import Rect

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Игровой объект."""

    position: tuple[int, int]
    body_color: tuple[int, int, int]

    def __init__(self):
        """Конструктор класса GameObject."""
        self.position = (0, 0)
        self.body_color = BOARD_BACKGROUND_COLOR

    def draw(self):
        """Отрисовать игровой объект."""
        ...


class Apple(GameObject):
    """Игровой объект - яблоко."""

    def __init__(self):
        """Конструктор класса Apple."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.prev_position = None

    def randomize_position(self, blacklist: list[Rect] = []):
        """Устанавливает случайное положение яблока на игровом поле."""
        self.prev_position = self.position
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

        if len(blacklist) > 0:
            rect = Rect(self.position, (GRID_SIZE, GRID_SIZE))
            while any([x.colliderect(rect) for x in blacklist]):
                self.randomize_position([])
                rect = Rect(self.position, (GRID_SIZE, GRID_SIZE))

    def draw(self):
        """Отрисовать яблоко."""
        rect = Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        if self.prev_position:
            rect = Rect(self.prev_position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect, 1)
            self.prev_position = None


class Snake(GameObject):
    """Игровой объект - змейка."""

    next_direction: tuple[int, int] | None

    def __init__(self, head_position: tuple[int, int] = (0, 0)):
        """Конструктор класса Snake."""
        super().__init__()
        self.prev_snake = None

        self.prev_length = 1
        self.length = 1

        self.head_position = head_position
        self.positions = [head_position]
        self.last = None
        self.direction = RIGHT
        self.next_direction = None

        self.body_color = SNAKE_COLOR

    def get_head_position(self) -> tuple[int, int]:
        """Получить координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновить направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновить позицию змейки."""
        head = self.get_head_position()
        self.positions.insert(0, (
            (head[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (head[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT,
        ))
        if self.prev_length == self.length:
            self.last = self.positions.pop()
        self.prev_length = self.length

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        prev_snake = Snake()
        prev_snake.prev_length = self.prev_length
        prev_snake.length = self.length
        prev_snake.positions = self.positions
        prev_snake.last = self.last
        prev_snake.direction = self.direction
        prev_snake.next_direction = self.next_direction
        prev_snake.body_color = self.body_color
        self.prev_snake = prev_snake

        self.prev_length = 1
        self.length = 1
        self.positions = [self.head_position]
        self.last = None
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR

    def draw(self):
        """Отрисовать змейку."""
        # Затирание прошлой змейки (до сброса)
        if self.prev_snake:
            for position in self.prev_snake.positions:
                rect = (Rect(position, (GRID_SIZE, GRID_SIZE)))
                pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
            if self.prev_snake.last:
                last_rect = Rect(self.prev_snake.last, (GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            self.prev_snake = None

        # Отрисовка тела змейки
        for position in self.positions[:-1]:
            rect = (Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def main():
    """Точка входа программы."""
    pygame.init()
    screen.fill(BOARD_BACKGROUND_COLOR)

    snake = Snake((GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE))
    blacklist = [Rect(x, (GRID_SIZE, GRID_SIZE)) for x in snake.positions]

    apple = Apple()
    apple.randomize_position(blacklist)
    apple.prev_position = None

    while True:
        handle_keys(snake)
        clock.tick(SPEED)

        snake.update_direction()
        snake.move()

        apple_rect = Rect(apple.position, (GRID_SIZE, GRID_SIZE))
        snake_head_rect = Rect(snake.get_head_position(),
                               (GRID_SIZE, GRID_SIZE))
        snake_body_rects = \
            [Rect(x, (GRID_SIZE, GRID_SIZE)) for x in snake.positions[1:]]

        if apple_rect.colliderect(snake_head_rect):
            # Проверка на столкновение с яблоком
            blacklist = [snake_head_rect, *snake_body_rects]
            snake.length += 1
            apple.randomize_position(blacklist)
        elif any([x.colliderect(snake_head_rect) for x in snake_body_rects]):
            # Проверка на столкновение с телом
            snake.reset()
            new_head = Rect(snake.get_head_position(), (GRID_SIZE, GRID_SIZE))
            apple.randomize_position([new_head])

        apple.draw()
        snake.draw()

        pygame.display.update()


def handle_keys(game_object: Snake):
    """Обработка нажатий клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


if __name__ == '__main__':
    main()
