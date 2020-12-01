import random
import json
from copy import deepcopy

import pathlib
from itertools import product
from typing import List, Optional, Tuple

# pylint: disable=no-member
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

Cell = Tuple[int, int]
Cells = List[int]
Grid = List[Cells]


class GameOfLife:
    def __init__(
        self, size: Tuple[int, int], randomize: bool = True, max_generations: float = float("inf")
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        if randomize:
            grid = [[random.randint(0, 1) for ci in range(self.cols)] for ci in range(self.rows)]
        else:
            grid = [[0] * self.cols for ci in range(self.rows)]
        return grid

    def get_neighbours(self, cell: Cell) -> Cells:
        sosedi = []
        for p in range(-1, 2):
            for r in range(-1, 2):
                if p == 0 and r == 0:
                    continue
                if 0 <= cell[0] + p < len(self.curr_generation) and 0 <= cell[1] + r < len(
                    self.curr_generation[0]
                ):
                    sosedi.append(self.curr_generation[cell[0] + p][cell[1] + r])
        return sosedi

    def get_next_generation(self) -> Grid:
        vihod = deepcopy(self.curr_generation)
        for p in range(len(vihod)):
            for r in range(len(vihod[p])):
                plus = sum(self.get_neighbours((p, r)))
                if plus == 2 and self.curr_generation[p][r] == 1 or plus == 3:
                    vihod[p][r] = 1
                else:
                    vihod[p][r] = 0
        return vihod

    def step(self) -> None:

        # Выполнить один шаг игры.

        self.prev_generation = deepcopy(self.curr_generation)
        self.curr_generation = self.get_next_generation()
        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:

        # Не превысило ли текущее число поколений максимально допустимое.

        if self.generations <= self.max_generations:
            return True
        else:
            return False

    @property
    def is_changing(self) -> bool:

        # Изменилось ли состояние клеток с предыдущего шага.

        if self.prev_generation != self.curr_generation:
            return True
        else:
            return False

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":

        # Прочитать состояние клеток из указанного файла.

        with open(filename, "r") as f:
            curr_generation = json.load(f)
        size = len(curr_generation), len(curr_generation[0])
        game = GameOfLife(size=size, randomize=False)
        game.curr_generation = curr_generation

        return game

    def save(self, filename: pathlib.Path) -> None:

        # Сохранить текущее состояние клеток в указанный файл.

        with open(filename, "w") as f:
            json.dump(self.curr_generation, fp=f)


def main():
    filename = "generation_{}.txt"

    def gen_path(step):
        return pathlib.Path(filename.format(step)).resolve()

    # New game
    game = GameOfLife(size=(48, 64))
    game.step()
    game.save(gen_path(0))

    # Game from save
    game = GameOfLife.from_file(gen_path(0))
    game.step()
    game.save(gen_path(1))


if __name__ == "__main__":
    main()
