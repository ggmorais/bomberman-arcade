from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import Game

import arcade

from src.animation import Animation
from src.sprites.blocks import Block, DestructibleBlock, BlockDestroy
from src.constants import *


class Bomb(arcade.Sprite):
    def __init__(self, game: Game, x: int, y: int, explosion_range: int = 1):
        super().__init__(center_x=x, center_y=y, scale=SPRITE_SCALE)

        self.game = game
        self.explosion_range = explosion_range
        self.animation = Animation()
        self.animation.add_state(
            "idle",
            [arcade.load_texture("./assets/sprites/Bomb.png", 16 * i, 0, 16, 16) for i in range(4)],
            fps=4,
        )
        self.animation.play("idle")
        self.texture = self.animation.get_current_texture()
        self.exploded = False

        self.timer = 2000

    def on_update(self, delta_time: float):
        if self not in self.game.bombs_collision and not self.collides_with_sprite(
            self.game.player
        ):
            self.game.bombs_collision.append(self)

        if self.timer <= 0 and not self.exploded:
            self.explode()
            return

        self.timer -= delta_time * 1000

        self.animation.update(delta_time)
        self.texture = self.animation.get_current_texture()

    def explode(self):
        if self.exploded:
            return

        if self in self.game.bombs_collision:
            self.game.bombs_collision.remove(self)
        self.exploded = True
        bomb_x, bomb_y = self.game.get_object_map_position(self)

        self.game.add_game_object(
            BombExplosion(self.game, self, bomb_x, bomb_y, explosion_type="Start")
        )

        explosions = [
            (bomb_x + 1, bomb_y),
            (bomb_x - 1, bomb_y),
            (bomb_x, bomb_y + 1),
            (bomb_x, bomb_y - 1),
        ]

        for x, y in explosions:
            for i in range(0, self.explosion_range):

                nx = x + i if x > bomb_x else x - i if x < bomb_x else x
                ny = y + i if y > bomb_y else y - i if y < bomb_y else y

                if self.game.get_game_object(nx, ny, Bomb) or self.game.get_game_object(
                    nx, ny, BombExplosion
                ):
                    explosion_type = "Middle"
                else:
                    explosion_type = "End" if i + 1 == self.explosion_range else "Middle"

                if self.game.get_game_object(nx, ny, Block):
                    break

                explosion = BombExplosion(
                    self.game,
                    self,
                    nx,
                    ny,
                    explosion_type=explosion_type,
                    flip_h=True if x < bomb_x else False,
                    flip_v=True if y > bomb_y else False,
                    flip_d=True if y != bomb_y else False,
                )
                self.game.add_game_object(explosion)

                destructible_block = self.game.get_game_object(nx, ny, DestructibleBlock)
                other_bomb = self.game.get_game_object(nx, ny, Bomb)

                if other_bomb:
                    other_bomb.explode()

                if destructible_block:
                    self.game.delete_game_object(destructible_block)
                    self.game.add_game_object(BlockDestroy(self.game, nx, ny))
                    break

        self.game.delete_game_object(self)


class BombExplosion(arcade.Sprite):
    def __init__(
        self,
        game: Game,
        bomb_origin,
        x: int,
        y: int,
        explosion_type: str = "Start",
        flip_h: bool = False,
        flip_v: bool = False,
        flip_d: bool = False,
    ):
        super().__init__(center_x=x, center_y=y, scale=SPRITE_SCALE)

        self.game = game
        self.bomb_origin = bomb_origin
        self.animation = Animation()
        self.animation.add_state(
            "explosion",
            [
                arcade.load_texture(
                    f"./assets/sprites/Explosion{explosion_type}.png",
                    16 * i,
                    0,
                    16,
                    16,
                    flipped_horizontally=flip_h,
                    flipped_vertically=flip_v,
                    flipped_diagonally=flip_d,
                )
                for i in range(8)
            ],
            fps=20,
            loop=False,
            anim_end_callback=lambda: self.game.delete_game_object(self),
        )

        self.animation.play("explosion")
        self.texture = self.animation.get_current_texture()

    def on_update(self, delta_time: float = 1 / 60):
        self.animation.update(delta_time)
        self.texture = self.animation.get_current_texture()
