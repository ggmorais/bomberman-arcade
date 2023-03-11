from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.sprites.player import Player
    from src.game import Game

import arcade

from src.constants import *


class Item(arcade.Sprite):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__(
            filename=f"./assets/sprites/ItemBlastRadius.png",
            center_x=x,
            center_y=y,
            scale=SPRITE_SCALE,
        )

        self.game = game

    def upgrade(self, player: Player):
        print("Upgrade fire range!")
        player.bomb_explosion_range += 1
        self.game.delete_game_object(self)
