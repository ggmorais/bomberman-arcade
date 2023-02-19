from __future__ import annotations


import random
import arcade

# Constants
SCREEN_WIDTH = 912  # 22 blocos
SCREEN_HEIGHT = 720  # 14 blocos
SCREEN_TITLE = "Bomberman"
SPRITE_SCALE = 3
MOVEMENT_SPEED = 3

OBJECTS_MAP = {}
# DESIGN_MAP = """
#     XXXXXXXXXXXXXXXXXXXXXX
#     XBBBBBBBBBBBBBBBBBBBBX
#     XB B B B B B B B B BBX
#     XB                  BX
#     XBB B B B B B B B B BX
#     XB                  BX
#     XB B B B B B B B B BBX
#     XB                  BX
#     XBB B B B B B B B B BX
#     XB                  BX
#     XB B B B B B B B B BBX
#     XB                  BX
#     XBBBBBBBBBBBBBBBBBBBBX
#     XXXXXXXXXXXXXXXXXXXXXX
#     """.strip()
# DESIGN_MAP = """
#     XXXXXXXXXXXXXXXXXX
#     XBBBBBBBBBBBBBBBBX
#     XB B B B B B B BBX
#     XB              BX
#     XBB B B B B B B BX
#     XB              BX
#     XB B B B B B B BBX
#     XB              BX
#     XBB B B B B B B BX
#     XB              BX
#     XB B B B B B B BBX
#     XB              BX
#     XBBBBBBBBBBBBBBBBX
#     XXXXXXXXXXXXXXXXXX
#     """.strip()
DESIGN_MAP = """
    XXXXXXXXXXXXXXXXXXX
    XBBBBBBBBBBBBBBBBBX
    XB               BX
    XB B B B B B B B BX
    XB               BX
    XB B B B B B B B BX
    XB               BX
    XB B B B B B B B BX
    XB               BX
    XB B B B B B B B BX
    XB               BX
    XB B B B B B B B BX
    XB               BX
    XBBBBBBBBBBBBBBBBBX
    XXXXXXXXXXXXXXXXXXX
    """.strip()


from dataclasses import dataclass, field


class Animation:
    def __init__(self):
        self.states = {}
        self.current_state = None
        self.current_frame = 0
        self.anim_timer = 0
        self.total_timer = 0

    def play(self, name: str):
        if self.current_state == name:
            return
        self.current_state = name
        self.current_frame = 0

    def add_state(self, name: str, textures: list[arcade.Texture], fps: int = 1):
        self.states[name] = {"fps": fps, "textures": textures}

    def get_current_texture(self) -> arcade.Texture:
        return self.states[self.current_state]["textures"][self.current_frame]

    def update(self, delta_time: float):
        state = self.states[self.current_state]

        if len(state["textures"]) == 1:
            return

        self.total_timer += delta_time
        self.total_timer = self.total_timer % 60
        time_diff = self.total_timer - self.anim_timer

        if time_diff * 1000 >= int(1000 / state["fps"]):
            self.anim_timer = self.total_timer

            if self.current_frame + 1 == len(state["textures"]):
                self.current_frame = 0
            else:
                self.current_frame += 1


class Bomb(arcade.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__(center_x=x, center_y=y, scale=SPRITE_SCALE)

        self.animation = Animation()
        self.animation.add_state(
            "idle",
            [arcade.load_texture("./assets/sprites/Bomb.png", 16 * i, 0, 16, 16) for i in range(4)],
            fps=4,
        )
        self.animation.play("idle")
        self.texture = self.animation.get_current_texture()

        self.timer = 1000

    def on_update(self, delta_time: float):
        self.animation.update(delta_time)
        self.texture = self.animation.get_current_texture()


class Player(arcade.Sprite):
    def __init__(self, game: Game, x: int, y: int):
        super().__init__(center_x=x, center_y=y, scale=SPRITE_SCALE)

        self.game = game
        self.animation = Animation()

        self.spawn_bomb_timer = 400

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

    def get_map_position(self):
        return int((self.center_x - 5) / 48), int((self.center_y - 5) / 48)

    def on_update(self, delta_time: float, keys_pressed: set = ()):
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

        if "SPACE" in keys_pressed and self.spawn_bomb_timer >= 400:
            if not self.game.get_game_object(*self.get_map_position(), Bomb):
                self.game.add_game_object(Bomb(*self.get_map_position()))
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

        self.animation.update(delta_time)
        self.texture = self.animation.get_current_texture()


class Block(arcade.Sprite):
    def __init__(self, x: int, y: int, name: str = "Block"):
        super().__init__(
            filename=f"./assets/sprites/{name}.png",
            center_x=x,
            center_y=y,
            scale=SPRITE_SCALE,
        )

        self.block_type = name


class Item(arcade.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__(
            filename=f"./assets/sprites/ItemBlastRadius.png",
            center_x=x,
            center_y=y,
            scale=SPRITE_SCALE,
        )


# @dataclass
# class GameState:
#     bombs = arcade.SpriteList()
#     blocks = arcade.SpriteList()
#     items = arcade.SpriteList()
#     player = Player(192, 190)

#     def __post_init__(self):
#         self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.game_objects[Block])


# GS = GameState()


class Game(arcade.Window):
    """Main application class."""

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.player = Player(self, 192, 190)
        self.game_objects = {
            Bomb: arcade.SpriteList(),
            Item: arcade.SpriteList(),
            Block: arcade.SpriteList(),
        }
        self.objects_map = {}

        for y, line in enumerate(reversed(DESIGN_MAP.split("\n"))):
            for x, block in enumerate(line.strip()):
                if block == "B":
                    self.add_game_object(Block(x, y, name="Block"))
                if block == " " and random.randint(0, 10) in range(4):
                    player_pos_x, player_pos_y = self.player.get_map_position()

                    if x not in (player_pos_x, player_pos_x - 1) or y not in (
                        player_pos_y,
                        player_pos_y + 1,
                    ):
                        self.add_game_object(Block(x, y, name="Brick"))

                        if random.randint(0, 20) == 1:
                            self.add_game_object(Item(x, y))

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.game_objects[Block])
        self.keys_enabled = ("SPACE", "RIGHT", "LEFT", "UP", "DOWN")
        self.keys_pressed = set()

        arcade.enable_timings()
        self.graph = arcade.PerfGraph(100, 100)

    def add_game_object(self, game_object: arcade.Sprite):
        self.game_objects[type(game_object)].append(game_object)
        self.objects_map.setdefault(game_object.position, []).append(game_object)
        game_object.center_x = game_object.center_x * 48 + 24
        game_object.center_y = game_object.center_y * 48 + 24

    def get_game_objects_by_type(self, object_type: arcade.Sprite):
        return self.game_objects[object_type]

    def get_all_game_objects(self):
        return self.game_objects.values()

    def get_game_object(self, x: int, y: int, object_type: arcade.Sprite):
        for item in self.objects_map.get((x, y), []):
            if isinstance(item, object_type):
                return item

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""

        self.clear()

        arcade.draw_rectangle_filled(
            (SCREEN_WIDTH) / 2,
            (SCREEN_HEIGHT) / 2,
            SCREEN_WIDTH - 80,
            SCREEN_HEIGHT - 80,
            arcade.csscolor.GREEN,
        )

        for obj in self.get_all_game_objects():
            obj.draw(pixelated=True)
            obj.draw_hit_boxes()

        self.player.draw(pixelated=True)
        self.player.draw_hit_box()

        self.graph.draw()

    def on_update(self, delta_time: float):
        self.player.on_update(delta_time, self.keys_pressed)
        self.game_objects[Bomb].on_update(delta_time)

        self.physics_engine.update()

        self.graph.update_graph(delta_time)
        self.graph.update()

    def on_key_press(self, symbol: int, modifiers: int):
        for key in self.keys_enabled:
            if symbol == getattr(arcade.key, key):
                self.keys_pressed.add(key)

    def on_key_release(self, symbol: int, modifiers: int):
        for key in self.keys_enabled:
            if symbol == getattr(arcade.key, key):
                self.keys_pressed.remove(key)


def main():
    window = Game()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
