import arcade
import pkg_resources

from Pokedex.views.instructionsView import InstructionsView


class MenuView(arcade.View):

    def __init__(self, WIDTH, HEIGHT):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT


    def on_show(self):
        arcade.set_background_color(arcade.color.GENERIC_VIRIDIAN)


    def on_draw(self):
        arcade.start_render()
        imagePath = pkg_resources.resource_filename("Pokedex", "imgs/pokemon-logo.png")
        image = arcade.load_texture(imagePath)
        scale = self.WIDTH / (image.width * 2)
        arcade.draw_scaled_texture_rectangle((self.WIDTH / 2),
                                             (self.HEIGHT / 1.5),
                                             image,
                                             scale)
        arcade.draw_text("Click to advance", self.WIDTH / 2, self.HEIGHT / 4,
                         arcade.color.AMARANTH_PINK, font_size=20, anchor_x="center")
        arcade.finish_render()


    def on_mouse_press(self, _x, _y, _button, _modifiers):
        instructions = InstructionsView(self.WIDTH, self.HEIGHT)
        self.window.show_view(instructions)