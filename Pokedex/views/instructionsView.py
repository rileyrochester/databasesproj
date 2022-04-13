import arcade
import arcade.gui

from Pokedex.views.compView import CompView
from Pokedex.views.pokedexView import PokedexView


class InstructionsView(arcade.View):

    def __init__(self, WIDTH, HEIGHT):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

    def on_show(self):
        arcade.set_background_color(arcade.color.FLORAL_WHITE)

    def on_draw(self):
        arcade.start_render()

        # instructions
        arcade.Text("    This application may be used as both a classic Pokédex and to compute battle strategies. "
                         "To use the Pokédex, simply arrow through the entries, or search by name, id, or type. "
                         "To measure up a prospective battle, choose up to 6 pokémon to populate your team, "
                         "up to 6 pokémon to populate the opposing team, and select the computation you'd like to see. ",
                    400,
                    500,
                    arcade.color.BLACK,
                    font_size=16,
                    width=600,
                    font_name=("courier new"),
                    anchor_x="center",
                    multiline=True)\
            .draw()

        # buttons
        blueStyle = {
            "font_name": ("courier new"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": arcade.color.BLUEBONNET,
            "bg_color": arcade.color.BLUE_BELL,

            # used if button is pressed
            "bg_color_pressed": arcade.color.BLUEBONNET,
            "border_color_pressed": arcade.color.BLUE_SAPPHIRE,  # also used when hovered
            "font_color_pressed": arcade.color.BLACK,
        }

        redStyle = {
            "font_name": ("courier new"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": arcade.color.BARN_RED,
            "bg_color": arcade.color.MEDIUM_RED_VIOLET,

            # used if button is pressed
            "bg_color_pressed": arcade.color.RED_VIOLET,
            "border_color_pressed": arcade.color.BARN_RED,  # also used when hovered
            "font_color_pressed": arcade.color.BLACK,
        }

        # Create a vertical BoxGroup to align buttons
        v_box = arcade.gui.UIBoxLayout(space_between=20)

        # Create the buttons
        pokedexBtn = arcade.gui.UIFlatButton(text="Pokédex", width=200, style=blueStyle)
        comptrBtn = arcade.gui.UIFlatButton(text="Battle Comparator", width=200, style=redStyle)

        v_box.add(pokedexBtn)
        v_box.add(comptrBtn)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_y=-125,
                child=v_box)
        )

        # handle clicks
        @pokedexBtn.event("on_click")
        def on_click_flatbutton(event):
            game_view = PokedexView(self.WIDTH, self.HEIGHT)
            self.window.show_view(game_view)

        @comptrBtn.event("on_click")
        def on_click_flatbutton(event):
            game_view = CompView(self.WIDTH, self.HEIGHT)
            self.window.show_view(game_view)

        # draws buttons
        self.manager.draw()

        arcade.finish_render()
