import arcade
import pkg_resources

from Pokedex.views.instructionsView import InstructionsView


class TitleScreenView(arcade.View):

    def __init__(self, WIDTH, HEIGHT):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT


    def on_show(self):
        arcade.set_background_color(arcade.color.GENERIC_VIRIDIAN)


    def on_draw(self):
        arcade.start_render()

        logoPath = pkg_resources.resource_filename("Pokedex", "imgs/pokemon-logo.png")
        logo = arcade.load_texture(logoPath)
        logoScale = self.WIDTH / (logo.width * 2)
        arcade.draw_scaled_texture_rectangle((self.WIDTH / 2) - 15,
                                             (self.HEIGHT / 1.5) + 50,
                                             logo,
                                             logoScale)

        spritePath = pkg_resources.resource_filename("Pokedex", "imgs/bulbasaur.png")
        sprite = arcade.load_texture(spritePath)
        spriteScale = self.WIDTH / (sprite.width * 6)
        arcade.draw_scaled_texture_rectangle((self.WIDTH / 2) - 10,
                                             (self.HEIGHT / 2) - 80,
                                             sprite,
                                             spriteScale)

        arcade.draw_text("Pokédex 2: the SQL", self.WIDTH / 2, 340,
                         arcade.color.BLACK, font_size=16,
                         font_name=("courier new"), anchor_x="center")

        arcade.draw_text(" A Battle Comparator", self.WIDTH / 2, 315,
                         arcade.color.BLACK, font_size=16,
                         font_name=("courier new"), anchor_x="center")

        arcade.draw_text("Click to advance", self.WIDTH / 2, 100,
                          arcade.color.AMARANTH_PINK, font_size=18,
                          font_name=("courier new"), anchor_x="center")

        arcade.draw_text("©2022 Riley Rochester & Medha Shah", self.WIDTH / 2, 25,
                         arcade.color.BLACK, font_size=11,
                          font_name=("courier new"), anchor_x="center")

        arcade.finish_render()


    def on_mouse_press(self, _x, _y, _button, _modifiers):
        instructions = InstructionsView(self.WIDTH, self.HEIGHT)
        self.window.show_view(instructions)