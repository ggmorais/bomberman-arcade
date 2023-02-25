import arcade


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

    def add_state(
        self,
        name: str,
        textures: list[arcade.Texture],
        fps: int = 1,
        loop: bool = True,
        anim_end_callback: callable = None,
    ):
        self.states[name] = {
            "fps": fps,
            "textures": textures,
            "loop": loop,
            "callback": anim_end_callback,
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

        if int(time_diff * 1000) >= int(1000 / state["fps"]):
            self.anim_timer = self.total_timer

            if self.current_frame + 1 == len(state["textures"]):
                if not state["loop"]:
                    if state["callback"]:
                        state["callback"]()
                    return

                self.current_frame = 0
            else:
                self.current_frame += 1
