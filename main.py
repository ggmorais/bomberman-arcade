import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Bomberman"
SPRITE_SCALE = 8


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
        self.states[name] = {
            "fps": fps,
            "textures": textures
        }

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
    def __init__(self):
        super().__init__(center_x=200, center_y=200, scale=SPRITE_SCALE)

        self.animation = Animation()
        self.animation.add_state("idle", [
            arcade.load_texture("./assets/sprites/Bomb.png", 16 * i, 0, 16, 16)
            for i in range(4)
        ], fps=4)
        self.animation.play("idle")
        self.texture = self.animation.get_current_texture()

    def on_update(self, delta_time: float):
        self.animation.update(delta_time)
        self.texture = self.animation.get_current_texture()


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(center_x=200, center_y=200, scale=SPRITE_SCALE)

        self.animation = Animation()
        
        # Horizontal walking/idle animations
        self.animation.add_state("idle_right", [
            arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 0, 72, 16, 24)
        ])
        self.animation.add_state("walk_right", [
            arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 16 * i, 72, 16, 24)
            for i in range(1, 4)
        ], fps=4)
        self.animation.add_state("idle_left", [
            arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 0, 48, 16, 24)
        ])
        self.animation.add_state("walk_left", [
            arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 16 * i, 48, 16, 24)
            for i in range(1, 4)
        ], fps=4)

        # Vertical walking/idle animations
        self.animation.add_state("idle_up", [
            arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 0, 0, 16, 24)
        ])
        self.animation.add_state("walk_up", [
            arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 16 * i, 0, 16, 24)
            for i in range(1, 4)
        ], fps=4)
        self.animation.add_state("idle_down", [
            arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 0, 24, 16, 24)
        ])
        self.animation.add_state("walk_down", [
            arcade.load_texture("./assets/sprites/PlayerWhiteWalk.png", 16 * i, 24, 16, 24)
            for i in range(1, 4)
        ], fps=4)

        self.animation.play("idle_right")
        self.texture = self.animation.get_current_texture()

        # Change the hitbox to fill only the bottom part of player's body
        self.set_hit_box([
            [-5, -10],  # left bottom x, y
            [5, -10],   # right bottom x, y
            [5, 0],     # right top x, y
            [-5, 0]     # left top x, y
        ])

    def on_update(self, delta_time: float):
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


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.bombs = arcade.SpriteList()
        self.bombs.append(Bomb())

        self.player = Player()

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.bombs)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""

        self.clear()
        # Code to draw the screen goes here

        self.bombs.draw(pixelated=True)
        self.bombs.draw_hit_boxes()

        self.player.draw(pixelated=True)
        self.player.draw_hit_box()

    def on_update(self, delta_time: float):
        if self.player.collides_with_list(self.bombs):
            print("colide!")

        self.player.on_update(delta_time)
        self.bombs.on_update(delta_time)

        self.physics_engine.update()
        
    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RIGHT:
            self.player.change_x = 5
        elif symbol == arcade.key.LEFT:
            self.player.change_x = -5
        elif symbol == arcade.key.UP:
            self.player.change_y = 5
        elif symbol == arcade.key.DOWN:
            self.player.change_y = -5

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol in (arcade.key.RIGHT, arcade.key.LEFT):
            self.player.change_x = 0
        if symbol in (arcade.key.UP, arcade.key.DOWN):
            self.player.change_y = 0


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()