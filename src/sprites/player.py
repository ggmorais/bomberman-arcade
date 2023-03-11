from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import Game

import arcade

from src.sprites.bombs import Bomb, BombExplosion
from src.sprites.items import Item
from src.animation import Animation
from src.constants import *


class Player(arcade.Sprite):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__(center_x=x, center_y=y, scale=SPRITE_SCALE)

        self.game = game
        self.animation = Animation()
        self.bombs_limit = 1
        self.bombs_quantity = 0
        self.bomb_explosion_range = 1
        self.spawn_bomb_timer = 400
        self.is_dead = False
        self.lifes = 3
        self.limit_invulnerable_timer = 1500
        self.invulnerable_timer = self.limit_invulnerable_timer

        # Horizontal walking/idle animations
        self.animation.add_state(
            "idle_right",
            [arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 0, 72, 16, 24)],
        )
        self.animation.add_state(
            "walk_right",
            [
                arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 16 * i, 72, 16, 24)
                for i in range(1, 4)
            ],
            fps=4,
        )
        self.animation.add_state(
            "idle_left",
            [arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 0, 48, 16, 24)],
        )
        self.animation.add_state(
            "walk_left",
            [
                arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 16 * i, 48, 16, 24)
                for i in range(1, 4)
            ],
            fps=4,
        )

        # Vertical walking/idle animations
        self.animation.add_state(
            "idle_up",
            [arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 0, 0, 16, 24)],
        )
        self.animation.add_state(
            "walk_up",
            [
                arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 16 * i, 0, 16, 24)
                for i in range(1, 4)
            ],
            fps=4,
        )
        self.animation.add_state(
            "idle_down",
            [arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 0, 24, 16, 24)],
        )
        self.animation.add_state(
            "walk_down",
            [
                arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 16 * i, 24, 16, 24)
                for i in range(1, 4)
            ],
            fps=4,
        )

        self.animation.add_state(
            "die",
            [
                arcade.load_texture("./assets/sprites/PlayerWhiteDeath.png", 16 * i, 0, 16, 24)
                for i in range(1, 6)
            ],
            fps=4,
            loop=False,
            # anim_end_callback=
        )

        self.animation.play("idle_right")
        self.texture = self.animation.get_current_texture()

        # Change the hitbox to fill only the bottom part of player's body
        self.set_hit_box(
            [
                [-5, -10],  # left bottom x, y
                [5, -10],  # right bottom x, y
                [5, 0],  # right top x, y
                [-5, 0],  # left top x, y
            ]
        )

    def take_damage(self):
        if self.lifes == 1 and self.invulnerable_timer == self.limit_invulnerable_timer:
            self.die()
        elif self.lifes > 0 and self.invulnerable_timer == self.limit_invulnerable_timer:
            self.lifes -= 1
            self.invulnerable_timer -= 1

    def die(self):
        if not self.is_dead:
            self.animation.play("die")
            self.is_dead = True

    def get_map_position(self):
        return int((self.center_x - 5) / 48), int((self.center_y - 5) / 48)

    def on_update(self, delta_time: float, keys_pressed: set = ()):
        if self.collides_with_list(self.game.get_game_objects_by_type(BombExplosion)):
            self.take_damage()

        self.animation.update(delta_time)
        self.texture = self.animation.get_current_texture()

        if self.is_dead:
            return

        self.spawn_bomb_timer += delta_time * 1000

        if "RIGHT" in keys_pressed:
            self.change_x = MOVEMENT_SPEED
        if "LEFT" in keys_pressed:
            self.change_x = -MOVEMENT_SPEED

        if "RIGHT" not in keys_pressed and "LEFT" not in keys_pressed:
            self.change_x = 0
        elif "RIGHT" in keys_pressed and "LEFT" in keys_pressed:
            self.change_x = 0

        if "UP" in keys_pressed:
            self.change_y = MOVEMENT_SPEED
        if "DOWN" in keys_pressed:
            self.change_y = -MOVEMENT_SPEED

        if "UP" not in keys_pressed and "DOWN" not in keys_pressed:
            self.change_y = 0
        elif "UP" in keys_pressed and "DOWN" in keys_pressed:
            self.change_y = 0

        if (
            "SPACE" in keys_pressed
            and self.spawn_bomb_timer >= 400
            and not self.game.get_game_object(*self.get_map_position(), Bomb)
            and len(self.game.get_game_objects_by_type(Bomb)) < self.bombs_limit
        ):
            self.game.add_game_object(
                Bomb(self.game, *self.get_map_position(), self.bomb_explosion_range)
            )
            self.spawn_bomb_timer = 0

        if self.velocity[0] > 0:
            self.animation.play("walk_right")
        elif self.velocity[0] < 0:
            self.animation.play("walk_left")
        elif self.velocity[1] > 0:
            self.animation.play("walk_up")
        elif self.velocity[1] < 0:
            self.animation.play("walk_down")
        else:
            self.animation.play(self.animation.current_state.replace("walk", "idle"))

        items = self.collides_with_list(self.game.get_game_objects_by_type(Item))

        for item in items:
            item.upgrade(self)

        if self.invulnerable_timer != self.limit_invulnerable_timer:
            self.invulnerable_timer -= delta_time * 1000

            if int(self.invulnerable_timer) // 100 % 2 == 0:
                self.alpha = 80
            else:
                self.alpha = 255

            if self.invulnerable_timer <= 0:
                self.invulnerable_timer = self.limit_invulnerable_timer
                self.alpha = 255
