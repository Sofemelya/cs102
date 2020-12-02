import random
import typing as tp
from copy import deepcopy
import pygame  # type: ignore
from pygame.locals import *  # type: ignore

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self, width: int = 640, height: int = 480, cell_size: int = 10, speed: int = 10
    ) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = width, height
        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали
        self.cell_width = self.width // self.cell_size
        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры
        self.speed = speed

        self.grid = self.create_grid()

    def draw_lines(self) -> None:
        # Отрисовать сетку
        for absc in range(0, self.width, self.cell_size):
            pygame.draw.line(
                self.screen, pygame.Color("black"), (absc, 0), (absc, self.height)
            )
        for ordin in range(0, self.height, self.cell_size):
            pygame.draw.line(
                self.screen, pygame.Color("black"), (0, ordin), (self.width, ordin)
            )

    def run(self) -> None:
        # Запустить игру
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))

        # Создание списка клеток
        self.grid = self.create_grid(randomize=True)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Отрисовка списка клеток
            self.draw_grid()
            self.draw_lines()
            # Выполнение одного шага игры (обновление состояния ячеек)
            self.grid = self.get_next_generation()

            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()

    def create_grid(self, randomize: bool = False) -> Grid:
        if randomize:
            grid = [
                [random.randint(0, 1) for ci in range(self.cell_width)]
                for ci in range(self.cell_height)
            ]
        else:
            grid = [[0] * self.cell_width for ci in range(self.cell_height)]
        return grid

    def draw_grid(self) -> None:
        # Отрисовка списка клеток с закрашиванием их в соответствующе цвета.
        for p in range(len(self.grid)):
            for r in range(len(self.grid[p])):
                if self.grid[p][r] == 1:
                    cell_colour = pygame.Color("green")
                else:
                    cell_colour = pygame.Color("white")
                squire = pygame.Rect(
                    r * self.cell_size,
                    p * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                pygame.draw.rect(self.screen, cell_colour, squire)

    def get_neighbours(self, cell: Cell) -> Cells:
        sosedi = []
        for p in range(-1, 2):
            for r in range(-1, 2):
                if p == 0 and r == 0:
                    continue
                if 0 <= cell[0] + p < len(self.grid) and 0 <= cell[1] + r < len(
                    self.grid[0]
                ):
                    sosedi.append(self.grid[cell[0] + p][cell[1] + r])
        return sosedi

    def get_next_generation(self) -> Grid:
        vihod = deepcopy(self.grid)
        for p in range(len(vihod)):
            for r in range(len(vihod)):
                plus = sum(self.get_neighbours((p, r)))
                if plus == 2 and self.grid[p][r] == 1 or plus == 3:
                    vihod[p][r] = 1
                else:
                    vihod[p][r] = 0
        return vihod


if __name__ == "__main__":
    game = GameOfLife(320, 240, 20)
    game.run()
