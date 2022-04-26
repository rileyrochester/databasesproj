#!/usr/bin/python3

import sys
import arcade
import arcade.gui
import pkg_resources
import pymysql

# from pokemon import Pokemon

WIDTH = 800
HEIGHT = 600
TITLE = "Pokédex 2: the SQL"
pokedex = dict()
USERPARTY = []
ADVPARTY = []


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

    def on_show(self):
        arcade.set_background_color(arcade.color.FLORAL_WHITE)
        self.manager.enable()

    def on_draw(self):
        arcade.start_render()

        # instructions
        arcade.Text("    This application may be used as both a classic Pokédex and to compute battle strategies. "
                    "To use the Pokédex, simply keyboard arrow through the entries, or search by name or id. "
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

        # Create a horizontal BoxGroup to align buttons
        v_box = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

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
            game_view = GetInfoView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

        # draws buttons
        self.manager.draw()

        arcade.finish_render()

    def on_hide_view(self):
        self.manager.disable()


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
        self.conn = None
        self.cur = None
        self.pokemon = (1, "bulbasaur", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.text = ''

    def on_show(self):
        arcade.set_background_color(arcade.color.FLORAL_WHITE)
        self.manager.enable()

    def on_draw(self):
        self.manager.clear()
        arcade.start_render()
        self.drawDexBase()
        self.renderPokemon()
        arcade.draw_text(self.text, 225, 140, arcade.color.GREEN, 20, anchor_x='center')
        arcade.draw_text("start typing your search query or keyboard arrow through results", 300, 50,
                         arcade.color.BLACK_LEATHER_JACKET, 10, anchor_x='center')
        self.renderMenuButton(250, 250)
        self.manager.draw()
        arcade.finish_render()

    def on_hide_view(self):
        self.manager.disable()

    def drawDexBase(self):
        imagePath = pkg_resources.resource_filename("Pokedex", "imgs/pokedex.png")
        image = arcade.load_texture(imagePath)
        scale = self.WIDTH / image.width
        arcade.draw_lrwh_rectangle_textured(40, 0, 700, 600, image, scale)
        arcade.draw_text("type:", 470, 155, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text("total:", 468, 205, arcade.color.BLACK, 8, font_name="courier new")
        arcade.draw_text("hp:", 480, 290, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text("atk:", 550, 298, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text("sp atk:", 547, 288, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text("def:", 550, 268, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text("sp def:", 547, 258, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text("speed:", 470, 260, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text("generation", 125, 150, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text("legendary:", 200, 230, arcade.color.BLACK, 8, font_name="courier new")

    def renderPokemon(self):
        self.mySqlConnect()
        self.loadPokemon()
        self.closeSqlConnection()

        spritePath = pkg_resources.resource_filename("Pokedex", f"imgs/pokemon/{self.pokemon[0][0]}.png")
        sprite = arcade.load_texture(spritePath)
        spriteScale = self.WIDTH / (sprite.width * 8)
        arcade.draw_scaled_texture_rectangle(250,
                                             300,
                                             sprite,
                                             spriteScale)

        info = f"{self.pokemon[0][0]} {self.pokemon[0][1]}"

        infoArea = arcade.gui.UITextArea(x=480,
                                         y=330,
                                         text=info,
                                         font_size=16,
                                         font_name=("courier new"),
                                         text_color=arcade.color.WHITE)
        self.manager.add(infoArea)

        arcade.draw_text(f"{self.pokemon[0][2]}",  # "type 1:",
                         490, 142, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][3]}",  # "type 2:",
                         605, 142, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][4]}",  # "total:",
                         513, 205, arcade.color.BLACK, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][5]}",  # "hp:",
                         517, 290, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][6]}",  # "atk:",
                         603, 290, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][8]}",  # "sp atk:",
                         645, 290, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][7]}",  # "def:",
                         603, 260, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][9]}",  # "sp def:",
                         645, 260, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][10]}",  # "speed:",
                         517, 260, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][11]}",  # "generation",
                         148, 175, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][12]}",  # "legendary:",
                         270, 230, arcade.color.BLACK, 8, font_name="courier new")

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

    def on_key_press(self, key, modifiers):
        # arrow right
        if key == arcade.key.RIGHT:
            # note : max should be 721 but workbench is fucking stupid and trying to import
            # a csv is like trying to scrape plastic off a frying pan
            if self.pid == 663:
                self.pid = 1
            else:
                self.pid += 1

        # arrow left
        elif key == arcade.key.LEFT:
            if self.pid == 1:
                self.pid = 663
            else:
                self.pid -= 1

        # enter aka search
        elif key == arcade.key.ENTER:
            searchQry = self.text.strip().title()
            self.text = ''
            self.mySqlConnect()
            self.loadPokemon(searchQry)
            self.closeSqlConnection()

        # backspace
        elif key == arcade.key.BACKSPACE:
            self.text = self.text[0: len(self.text) - 1]

        # search query
        else:
            self.text += chr(key)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.LEFT:
            self.renderPokemon()

    ### SQL INTERACTIONS ###
    def mySqlConnect(self):
        self.conn = pymysql.connect(
            host='localhost',
            user=self.sqlun,
            password=self.sqlpw,
            db='pokemon_server',
        )

        self.cur = self.conn.cursor()

    def loadPokemon(self, searchQry=None):
        if searchQry is not None:
            if searchQry.isnumeric():
                stmt = f"select * from pokemons where `#` = {searchQry};"
                self.pid = int(searchQry)
                currPid = True
            else:
                stmt = f"select * from pokemons where Name = \"{searchQry}\""
                currPid = False
        else:
            stmt = f"select * from pokemons where `#` = {self.pid};"
            currPid = True

        self.loadPokemonHelper(stmt, currPid)

    def loadPokemonHelper(self, stmt, currPid):
        if currPid and self.pid in pokedex:
            self.pokemon = pokedex.get(self.pid)
        else:
            self.cur.execute(stmt)
            self.pokemon = self.cur.fetchall()
            self.pid = self.pokemon[0][0]
            pokedex[self.pid] = self.pokemon

    def closeSqlConnection(self):
        self.cur.close()
        self.conn.close()


# GET INFO SCREEN
class GetInfoView(arcade.View):

    def __init__(self, WIDTH, HEIGHT, sqlun, sqlpw):
        super().__init__()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.sqlun = sqlun
        self.sqlpw = sqlpw
        self.conn = None
        self.cur = None
        self.manager = arcade.gui.UIManager()
        self.text = ""
        self.pokemon = ((1, "Bulbasaur", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.pid = 1

    def on_show(self):
        arcade.set_background_color(arcade.color.PAPAYA_WHIP)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        arcade.start_render()
        self.manager.clear()

        arcade.draw_text(
            f"type name or id of next party member : ",
            60, 520,
            arcade.color.BLACK_LEATHER_JACKET,
            18, 700,
            "center",
            "courier new",
        )
        arcade.draw_text(
            f"press ENTER to add to user party, press TAB to add to adversary party",
            170, 480,
            arcade.color.BLACK_LEATHER_JACKET,
            12, 400,
            "center",
            "courier new")
        arcade.draw_text(
            self.text,
            300, 400,
            arcade.color.BLACK_LEATHER_JACKET,
            20, 200,
            "center",
            "courier new")

        x = 0
        for pokemon in USERPARTY:
            arcade.draw_text(f"{pokemon[0]} : {pokemon[1]}",
                             80, 370 - (20 * x),
                             arcade.color.GENERIC_VIRIDIAN,
                             12)
            x += 1

        x = 0
        for pokemon in ADVPARTY:
            arcade.draw_text(f"{pokemon[0]} : {pokemon[1]}",
                             550, 370 - (20 * x),
                             arcade.color.ANTIQUE_RUBY,
                             12)
            x += 1

        self.drawBtns()
        self.manager.draw()

        arcade.finish_render()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER and len(USERPARTY) < 6:
            item = self.text.strip().title()
            self.loadPokemon(item)
            USERPARTY.append(self.pokemon[0])
            self.text = ''

        elif key == arcade.key.TAB and len(ADVPARTY) < 6:
            item = self.text.strip().title()
            self.loadPokemon(item)
            ADVPARTY.append(self.pokemon[0])
            self.text = ''

        elif key == arcade.key.BACKSPACE:
            self.text = self.text[0: len(self.text) - 1]

        else:
            self.text += chr(key)

    def on_update(self, delta_time):
        if len(USERPARTY) == 6 and len(ADVPARTY) == 6:
            game_view = CompView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

    def drawBtns(self):
        style1 = {
            "font_name": ("courier new"),
            "font_size": 12,
            "font_color": arcade.color.BLACK_LEATHER_JACKET,
            "border_width": 2,
            "border_color": arcade.color.PURPUREUS,
            "bg_color": arcade.color.PERSIAN_PINK,
        }
        style2 = {
            "font_name": ("courier new"),
            "font_size": 12,
            "font_color": arcade.color.BLACK_LEATHER_JACKET,
            "border_width": 2,
            "border_color": arcade.color.ALLOY_ORANGE,
            "bg_color": arcade.color.YELLOW_ROSE,
        }

        h_box = arcade.gui.UIBoxLayout(vertical=True, space_between=20)
        menuBtn = arcade.gui.UIFlatButton(text="Menu", width=200, style=style1)
        nextBtn = arcade.gui.UIFlatButton(text="NEXT", width=200, style=style2)

        menuBtn.on_click = self.on_click_menubutton
        nextBtn.on_click = self.on_click_next

        h_box.add(nextBtn)
        h_box.add(menuBtn)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_y=-150,
                child=h_box)
        )

    # handle clicks
    # @menuBtn.event("on_click")
    def on_click_menubutton(self, event):
        game_view = InstructionsView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
        self.window.show_view(game_view)

    # @nextBtn.event("on_click")
    def on_click_next(self, event):
        print(event)
        game_view = CompView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
        self.window.show_view(game_view)

    def loadPokemon(self, searchQry=None):
        self.mySqlConnect()
        if searchQry is not None:
            if searchQry.isnumeric():
                stmt = f"select * from pokemons where `#` = {searchQry};"
                self.pid = int(searchQry)
                currPid = True
            else:
                stmt = f"select * from pokemons where Name = \"{searchQry}\""
                currPid = False
        else:
            stmt = f"select * from pokemons where `#` = {self.pid};"
            currPid = True

        self.loadPokemonHelper(stmt, currPid)
        self.closeSqlConnection()

    def loadPokemonHelper(self, stmt, currPid):
        if currPid and self.pid in pokedex:
            self.pokemon = pokedex.get(self.pid)
        else:
            self.cur.execute(stmt)
            self.pokemon = self.cur.fetchall()
            self.pid = self.pokemon[0][0]
            pokedex[self.pid] = self.pokemon

    ### MYSQL CONNECTION ###
    def mySqlConnect(self):
        self.conn = pymysql.connect(
            host='localhost',
            user=self.sqlun,
            password=self.sqlpw,
            db='pokemon_server',
        )

        self.cur = self.conn.cursor()

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
        self.conn = None
        self.cur = None
        self.manager = arcade.gui.UIManager()
        self.pokemon = ((1, "Bulbasaur", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.text = ''
        self.pid = 1
        self.curWidgetXY = ()
        self.dialogueBox = None

    def on_show(self):
        arcade.set_background_color(arcade.color.ALMOND)
        self.manager.enable()

    def on_draw(self):
        arcade.start_render()
        self.manager.clear()
        self.drawBackground()
        self.establishWidgetSpace()
        self.renderMenuButton(320, -250)
        self.manager.draw()
        arcade.finish_render()

    def on_hide_view(self):
        self.manager.disable()

    def renderMenuButton(self, x, y):
        style = {
            "font_name": ("courier new"),
            "font_size": 12,
            "font_color": arcade.color.BLACK_LEATHER_JACKET,
            "border_width": 2,
            "border_color": arcade.color.PURPUREUS,
            "bg_color": arcade.color.PERSIAN_PINK,
        }
        v_box = arcade.gui.UIBoxLayout()
        menuBtn = arcade.gui.UIFlatButton(text="Menu", width=100, style=style)
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

    def drawBackground(self):
        # advBG
        arcade.create_rectangle_filled(200, 450, 400, 300, arcade.color.LIGHT_CRIMSON, 0).draw()

        # arcade.create_rectangle_filled(70, 495, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(190, 495, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(310, 495, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(70, 370, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(190, 370, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(310, 370, 100, 100, arcade.color.WHITE, 0).draw()

        # usrBG
        arcade.create_rectangle_filled(600, 450, 400, 300, arcade.color.LIGHT_MOSS_GREEN, 0).draw()

        # arcade.create_rectangle_filled(480, 70, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(600, 70, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(720, 70, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(480, 190, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(600, 190, 100, 100, arcade.color.WHITE, 0).draw()
        # arcade.create_rectangle_filled(720, 190, 100, 100, arcade.color.WHITE, 0).draw()

    def establishWidgetSpace(self):
        h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=0)
        left_box = arcade.gui.UIBoxLayout(space_between=0)
        right_box = arcade.gui.UIBoxLayout(space_between=0)

        left_box.add(self.topLeftWidget())
        left_box.add(self.bottomLeftWidget())

        right_box.add(self.topRightWidget())
        right_box.add(self.bottomRightWidget())

        h_box.add(left_box)
        h_box.add(right_box)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=h_box)
        )

    # top left widget : adversary party
    def topLeftWidget(self):
        advPartyLabel = arcade.gui.UITextArea(
            text="    Adversary Party",
            width=400,
            height=25,
            font_size=12,
            text_color=arcade.color.BLACK_LEATHER_JACKET,
            font_name="courier new")

        adversaryParty = arcade.gui.UIBoxLayout(x=0, y=300, space_between=20)
        advTopRow = arcade.gui.UIBoxLayout(vertical=False, space_between=20)
        advBottomRow = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        if len(ADVPARTY) > 0:
            advSprite1 = self.renderPokemon(ADVPARTY[0][0])
        else:
            advSprite1 = arcade.Sprite()
        if len(ADVPARTY) > 0:
            advSprite2 = self.renderPokemon(ADVPARTY[1][0])
        else:
            advSprite2 = arcade.Sprite()
        if len(ADVPARTY) > 0:
            advSprite3 = self.renderPokemon(ADVPARTY[2][0])
        else:
            advSprite3 = arcade.Sprite()
        if len(ADVPARTY) > 0:
            advSprite4 = self.renderPokemon(ADVPARTY[3][0])
        else:
            advSprite4 = arcade.Sprite()
        if len(ADVPARTY) > 0:
            advSprite5 = self.renderPokemon(ADVPARTY[4][0])
        else:
            advSprite5 = arcade.Sprite()
        if len(ADVPARTY) > 0:
            advSprite6 = self.renderPokemon(ADVPARTY[5][0])
        else:
            advSprite6 = arcade.Sprite()

        adv1 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=advSprite1))
        adv2 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=advSprite2))
        adv3 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=advSprite3))
        adv4 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=advSprite4))
        adv5 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=advSprite5))
        adv6 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=advSprite6))

        advTopRow.add(adv1)
        advTopRow.add(adv2)
        advTopRow.add(adv3)
        advBottomRow.add(adv4)
        advBottomRow.add(adv5)
        advBottomRow.add(adv6)

        adversaryParty.add(advPartyLabel)
        adversaryParty.add(advTopRow)
        adversaryParty.add(arcade.gui.UIPadding(child=advBottomRow, padding=(0, 0, 20, 0)))

        return adversaryParty

    # bottom left widget : calculations buttons
    def bottomLeftWidget(self):
        calcBox = arcade.gui.UIBoxLayout()
        calcLabel = arcade.gui.UITextArea(
            text="    Calculations: ",
            width=400,
            height=25,
            font_size=12,
            text_color=arcade.color.BLACK,
            font_name="courier new")

        style = {
            "font_name": ("courier new"),
            "font_size": 12,
            "font_color": arcade.color.BLACK_LEATHER_JACKET,
            "border_width": 2,
            "border_color": arcade.color.PURPUREUS,
            "bg_color": arcade.color.PERSIAN_PINK
        }

        typeAdvBtn = arcade.gui.UIFlatButton(text="Type Advantage", style=style)
        bestAdtnBtn = arcade.gui.UIFlatButton(text="Best Type Addition", style=style)
        calcBtnSpace = arcade.gui.UIPadding(
            child=arcade.gui.UIBoxLayout(
                space_between=20,
                vertical=False,
                children=(typeAdvBtn, bestAdtnBtn)),
            padding=(105, 40, 105, 40))

        calcBox.add(calcLabel)
        calcBox.add(calcBtnSpace)

        return calcBox

    # top right widget : user party
    def topRightWidget(self):
        myTeamLabel = arcade.gui.UILabel(
            text="    My Team",
            width=400,
            height=25,
            font_size=12,
            font_name="courier new",
            text_color=arcade.color.BLACK_LEATHER_JACKET)

        userParty = arcade.gui.UIBoxLayout(x=400, y=300, space_between=20)
        userTopRow = arcade.gui.UIBoxLayout(vertical=False, space_between=20)
        userBottomRow = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        if len(USERPARTY) > 0:
            userSprite1 = self.renderPokemon(USERPARTY[0][0])
        else:
            userSprite1 = arcade.Sprite()
        if len(USERPARTY) > 0:
            userSprite2 = self.renderPokemon(USERPARTY[1][0])
        else:
            userSprite2 = arcade.Sprite()
        if len(USERPARTY) > 0:
            userSprite3 = self.renderPokemon(USERPARTY[2][0])
        else:
            userSprite3 = arcade.Sprite()
        if len(USERPARTY) > 0:
            userSprite4 = self.renderPokemon(USERPARTY[3][0])
        else:
            userSprite4 = arcade.Sprite()
        if len(USERPARTY) > 0:
            userSprite5 = self.renderPokemon(USERPARTY[4][0])
        else:
            userSprite5 = arcade.Sprite()
        if len(USERPARTY) > 0:
            userSprite6 = self.renderPokemon(USERPARTY[5][0])
        else:
            userSprite6 = arcade.Sprite()

        user1 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=userSprite1))
        user2 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=userSprite2))
        user3 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=userSprite3))
        user4 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=userSprite4))
        user5 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=userSprite5))
        user6 = arcade.gui.UIBorder(child=arcade.gui.UISpriteWidget(sprite=userSprite6))

        userTopRow.add(user1)
        userTopRow.add(user2)
        userTopRow.add(user3)
        userBottomRow.add(user4)
        userBottomRow.add(user5)
        userBottomRow.add(user6)

        userParty.add(myTeamLabel)
        userParty.add(userTopRow)
        userParty.add(arcade.gui.UIPadding(child=userBottomRow, padding=(0, 0, 20, 0)))

        return userParty

    # bottom right widget : generated reports
    def bottomRightWidget(self):
        reportsBox = arcade.gui.UIBoxLayout()
        reportsLabel = arcade.gui.UITextArea(
            text="    Reports: ",
            width=400,
            height=25,
            font_size=12,
            text_color=arcade.color.BLACK,
            font_name="courier new")

        # TODO : text = sql procedure to get calc results
        text = "reports.............:("
        repsRes = arcade.gui.UITextArea(text=text, height=260)

        reportsBox.add(reportsLabel)
        reportsBox.add(repsRes)

        return reportsBox

    def renderPokemon(self, pid):
        spritePath = pkg_resources.resource_filename("Pokedex", f"imgs/pokemon/{pid}.png")
        tex = arcade.load_texture(spritePath)
        spriteScale = self.WIDTH / (tex.width * 8)
        return arcade.Sprite(spritePath, spriteScale)


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
