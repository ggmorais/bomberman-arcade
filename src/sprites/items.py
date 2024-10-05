from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.sprites.player import Player
    from src.game import Game

import arcade

from src.constants import *


class Item(arcade.Sprite):
    def __init__(self, game: Game, x: int, y: int, filename: str):
        super().__init__(
            filename=f"./assets/sprites/{filename}",
            center_x=x,
            center_y=y,
            scale=SPRITE_SCALE,
        )

        self.game = game

    def upgrade(self, player: Player):
        pass


class ItemBlastRadius(Item):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__(game, x, y, filename="ItemBlastRadius.png")

    def upgrade(self, player: Player):
        print("Upgrade fire range!")
        player.bomb_explosion_range += 1
        self.game.delete_game_object(self)


class ItemExtraBomb(Item):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__(game, x, y, filename="ItemExtraBomb.png")

    def upgrade(self, player: Player):
        print("Upgrade fire range!")
        player.bombs_limit += 1
        self.game.delete_game_object(self)


class ItemSpeedIncrease(Item):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__(game, x, y, filename="ItemSpeedIncrease.png")

    def upgrade(self, player: Player):
        print("Upgrade fire range!")
        player.movement_speed += 0.5
        self.game.delete_game_object(self)
