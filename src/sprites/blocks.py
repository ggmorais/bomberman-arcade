from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import Game

import arcade

from src.animation import Animation
from src.constants import *


class Block(arcade.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__(
            filename=f"./assets/sprites/Block.png",
            center_x=x,
            center_y=y,
            scale=SPRITE_SCALE,
        )


class DestructibleBlock(arcade.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__(
            filename=f"./assets/sprites/Brick.png",
            center_x=x,
            center_y=y,
            scale=SPRITE_SCALE,
        )


class BlockDestroy(arcade.Sprite):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__(center_x=x, center_y=y, scale=SPRITE_SCALE)

        self.game = game
        self.animation = Animation()
        self.animation.add_state(
            "idle",
            [
                arcade.load_texture("./assets/sprites/BrickDestroy.png", 16 * i, 0, 16, 16)
                for i in range(4)
            ],
            fps=10,
            loop=False,
            anim_end_callback=lambda: self.game.delete_game_object(self),
        )
        self.animation.play("idle")
        self.texture = self.animation.get_current_texture()

    def on_update(self, delta_time: float = 1 / 60):
        self.animation.update(delta_time)
        self.texture = self.animation.get_current_texture()


class Ground(arcade.Sprite):
    def __init__(self, game: Game, x: int, y: int, name: str = "Ground"):
        super().__init__(
            filename=f"./assets/sprites/{name}.png",
            center_x=x,
            center_y=y,
            scale=SPRITE_SCALE,
        )
        self.game = game
