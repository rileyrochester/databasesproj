import arcade


class CompView(arcade.View):

    def __init__(self, WIDTH, HEIGHT):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def on_show(self):
        arcade.set_background_color(arcade.color.PURPUREUS)

    def on_draw(self):
        arcade.start_render()