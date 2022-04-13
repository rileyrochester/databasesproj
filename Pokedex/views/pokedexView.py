import arcade
import pkg_resources


class PokedexView(arcade.View):

    def __init__(self, WIDTH, HEIGHT):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def on_show(self):
        arcade.set_background_color(arcade.color.FLORAL_WHITE)

    def on_draw(self):
        arcade.start_render()
        self.drawDexBase()
        arcade.finish_render()

    def drawDexBase(self):
        imagePath = pkg_resources.resource_filename("Pokedex", "imgs/pokedex.png")
        image = arcade.load_texture(imagePath)
        scale = self.WIDTH / image.width
        arcade.draw_lrwh_rectangle_textured(40, 0, 700, 600, image, scale)