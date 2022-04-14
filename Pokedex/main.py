#!/usr/bin/python3

import sys
import arcade
import arcade.gui
import pkg_resources
import pymysql

WIDTH = 800
HEIGHT = 600
TITLE = "Pokédex 2: the SQL"


### VIEWS ###

# HOME SCREEN
class TitleScreenView(arcade.View):

    def __init__(self, WIDTH, HEIGHT, sqlun, sqlpw):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.sqlun = sqlun
        self.sqlpw = sqlpw

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
        instructions = InstructionsView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
        self.window.show_view(instructions)


# INSTRUCTIONS / MENU SCREEN
class InstructionsView(arcade.View):

    def __init__(self, WIDTH, HEIGHT, sqlun, sqlpw):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.sqlun = sqlun
        self.sqlpw = sqlpw
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
                    multiline=True) \
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
            game_view = PokedexView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

        @comptrBtn.event("on_click")
        def on_click_flatbutton(event):
            game_view = CompView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

        # draws buttons
        self.manager.draw()

        arcade.finish_render()


# POKEDEX SCREEN
class PokedexView(arcade.View):

    def __init__(self, WIDTH, HEIGHT, sqlun, sqlpw):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.sqlun = sqlun
        self.sqlpw = sqlpw
        self.pid = 1
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.conn = None
        self.cur = None
        self.pokemon = dict()

    def on_show(self):
        arcade.set_background_color(arcade.color.FLORAL_WHITE)

    def on_draw(self):
        arcade.start_render()
        self.drawDexBase()
        self.renderPokemon()
        self.renderMenuButton(250, 250)
        arcade.finish_render()

    def drawDexBase(self):
        imagePath = pkg_resources.resource_filename("Pokedex", "imgs/pokedex.png")
        image = arcade.load_texture(imagePath)
        scale = self.WIDTH / image.width
        arcade.draw_lrwh_rectangle_textured(40, 0, 700, 600, image, scale)

    def renderPokemon(self):
        # self.mySqlConnect()
        # self.loadPokemon()
        # self.closeSqlConnection()

        spritePath = pkg_resources.resource_filename("Pokedex", "imgs/bulbasaur.png")
        sprite = arcade.load_texture(spritePath)
        spriteScale = self.WIDTH / (sprite.width * 8)
        arcade.draw_scaled_texture_rectangle(250,
                                             300,
                                             sprite,
                                             spriteScale)

        arcade.draw_text("My man", 550, 350,
                         arcade.color.WHITE, font_size=16,
                         font_name=("courier new"), anchor_x="center")

    def renderMenuButton(self, x, y):
        style = {
            "font_name": ("courier new"),
            "font_size": 15,
            "font_color": arcade.color.BLACK_LEATHER_JACKET,
            "border_width": 2,
            "border_color": arcade.color.PURPUREUS,
            "bg_color": arcade.color.PERSIAN_PINK,
        }
        v_box = arcade.gui.UIBoxLayout(space_between=20)
        menuBtn = arcade.gui.UIFlatButton(text="Menu", width=200, style=style)
        v_box.add(menuBtn)
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_x=x,
                align_y=y,
                child=v_box)
        )

        # handle clicks
        @menuBtn.event("on_click")
        def on_click_flatbutton(event):
            game_view = InstructionsView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

        self.manager.draw()

    ### SQL INTERACTIONS ###
    def mySqlConnect(self):
        self.conn = pymysql.connect(
            host='localhost',
            user=self.sqlun,
            password=self.sqlpw,
            db='pokedex',
        )

        self.cur = self.conn.cursor()

    def loadPokemon(self):
        stmt = f"select * from pokemon where id = {self.pid};"
        self.cur.execute(stmt, list(self.pokemon.values()))

        self.pokemon = self.cur.fetchall()
        print(self.pokemon)

    def closeSqlConnection(self):
        self.cur.close()
        self.conn.close()


# COMPARATOR SCREEN
class CompView(arcade.View):

    def __init__(self, WIDTH, HEIGHT, sqlun, sqlpw):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.sqlun = sqlun
        self.sqlpw = sqlpw
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

    def on_show(self):
        arcade.set_background_color(arcade.color.PURPUREUS)

    def on_draw(self):
        arcade.start_render()
        self.renderMenuButton(250, 250)
        arcade.finish_render()

    def renderMenuButton(self, x, y):
        style = {
            "font_name": ("courier new"),
            "font_size": 15,
            "font_color": arcade.color.BLACK_LEATHER_JACKET,
            "border_width": 2,
            "border_color": arcade.color.PURPUREUS,
            "bg_color": arcade.color.PERSIAN_PINK,
        }
        v_box = arcade.gui.UIBoxLayout(space_between=20)
        menuBtn = arcade.gui.UIFlatButton(text="Menu", width=200, style=style)
        v_box.add(menuBtn)
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_x=x,
                align_y=y,
                child=v_box)
        )

        # handle clicks
        @menuBtn.event("on_click")
        def on_click_flatbutton(event):
            game_view = InstructionsView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

        self.manager.draw()


### SCRIPTING ###

def main():
    # command line input
    args = sys.argv[1:]
    sqlun = args[0].strip()
    sqlpw = args[1].strip()

    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    titleScreenView = TitleScreenView(WIDTH, HEIGHT, sqlun, sqlpw)
    window.show_view(titleScreenView)
    arcade.run()


# ENTRY POINT
if __name__ == "__main__":
    main()
