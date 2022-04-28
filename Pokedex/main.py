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
userName = ""
userId = None
pokedex = dict()
# contains pokedex info regarding the types of pokemon on each team
USERPARTY = []
ADVPARTY = []
# contains teamId, etc of teamMembers for each team
userTeam = dict()
advTeam = dict()

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

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            game_view = PokedexView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)
        elif key == arcade.key.RIGHT:
            game_view = GetInfoView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

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
        self.pokemon = ((1, "bulbasaur", 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
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
        # arcade.draw_text("legendary:", 200, 230, arcade.color.BLACK, 8, font_name="courier new")

    def renderPokemon(self):
        self.loadPokemon()

        spritePath = pkg_resources.resource_filename("Pokedex", f"imgs/pokemon/{self.pokemon[0][0]}.png")
        sprite = arcade.load_texture(spritePath)
        spriteScale = self.WIDTH / (sprite.width * 8)
        arcade.draw_scaled_texture_rectangle(250,
                                             300,
                                             sprite,
                                             spriteScale)

        info = f"{self.pokemon[0][0]} {self.pokemon[0][1]}"

        infoArea = arcade.gui.UITextArea(x=475,
                                         y=335,
                                         width=250,
                                         height=45,
                                         text=info,
                                         font_size=16,
                                         font_name=("courier new"),
                                         text_color=arcade.color.WHITE,
                                         multiline=True)
        self.manager.add(infoArea)

        arcade.draw_text(f"{self.pokemon[0][3]}",  # "type 1:",
                         490, 142, arcade.color.WHITE, 8, font_name="courier new")
        # arcade.draw_text(f"{self.pokemon[0][3]}",  # "type 2:",
        #                  605, 142, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[1][1]}",  # "total:",
                         513, 205, arcade.color.BLACK, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[1][2]}",  # "hp:",
                         517, 290, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[1][3]}",  # "atk:",
                         603, 290, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[1][5]}",  # "sp atk:",
                         645, 290, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[1][4]}",  # "def:",
                         603, 260, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[1][6]}",  # "sp def:",
                         645, 260, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[1][7]}",  # "speed:",
                         517, 260, arcade.color.WHITE, 8, font_name="courier new")
        arcade.draw_text(f"{self.pokemon[0][2]}",  # "generation",
                         148, 175, arcade.color.WHITE, 8, font_name="courier new")
        # arcade.draw_text(f"{self.pokemon[0][12]}",  # "legendary:",
        #                  270, 230, arcade.color.BLACK, 8, font_name="courier new")
        pass

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
            # note : max should be 721 but workbench is stupid and trying to import
            # a csv is like trying to scrape plastic off a frying pan
            if self.pid == 648:
                self.pid = 1
            else:
                self.pid += 1

        # arrow left
        elif key == arcade.key.LEFT:
            if self.pid == 1:
                self.pid = 648
            else:
                self.pid -= 1

        # arrow up
        elif key == arcade.key.UP:
            game_view = InstructionsView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

        # enter aka search
        elif key == arcade.key.ENTER:
            searchQry = self.text.strip().title()
            self.text = ''
            self.loadPokemon(searchQry)

        # backspace
        elif key == arcade.key.BACKSPACE:
            self.text = self.text[0: len(self.text) - 1]

        # search query
        else:
            self.text += chr(key)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.RIGHT or key == arcade.key.LEFT:
            self.renderPokemon()

    def loadPokemon(self, searchQry=None):
        self.mySqlConnect()

        if searchQry is not None:
            if searchQry.isnumeric():
                self.pid = int(searchQry)

                if self.pid in pokedex:
                    self.pokemon = pokedex.get(self.pid)
                else:
                    self.cur.callproc('findPokemonByID', [self.pid])
                    self.pokemon = self.cur.fetchall()
                    self.pid = self.pokemon[0][0]

                    self.cur.callproc('findPokemonPowersByID', [self.pid])
                    powers = self.cur.fetchall()
                    self.pokemon += powers

                    pokedex[self.pid] = self.pokemon
            else:
                self.cur.callproc('findPokemonByName', [searchQry])
                self.pokemon = self.cur.fetchall()
                self.pid = self.pokemon[0][0]

                self.cur.callproc('findPokemonPowersByID', [self.pid])
                powers = self.cur.fetchall()
                self.pokemon += powers

                pokedex[self.pid] = self.pokemon
        else:
            if self.pid in pokedex:
                self.pokemon = pokedex.get(self.pid)
            else:
                self.cur.callproc('findPokemonByID', [self.pid])
                self.pokemon = self.cur.fetchall()
                # print(self.pokemon)
                self.pid = self.pokemon[0][0]

                self.cur.callproc('findPokemonPowersByID', [self.pid])
                powers = self.cur.fetchall()
                self.pokemon += powers

                pokedex[self.pid] = self.pokemon

        self.closeSqlConnection()

    ### SQL INTERACTIONS ###
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


# GET INFO SCREEN
# creates user (id=1) and adversary (id=2) teams in db
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
        self.pokemon = ((1, "Bulbasaur", 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
        self.pid = 1

    def on_show(self):
        arcade.set_background_color(arcade.color.ALMOND)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        arcade.start_render()
        self.manager.clear()

        arcade.draw_text(
            f"(1) Type your name and hit control : ",
            140, 550,
            arcade.color.BLACK_LEATHER_JACKET,
            12, 500,
            "center",
            "courier new")
        arcade.draw_text(
            f"(2) Type name or id of next party member, comma, an item from the list left (or \"none\"), comma, level. ",
            140, 525,
            arcade.color.BLACK_LEATHER_JACKET,
            12, 500,
            "center",
            "courier new")
        arcade.draw_text(
            f"(3) Press ENTER to add to user party, press TAB to add to adversary party. ",
            140, 470,
            arcade.color.BLACK_LEATHER_JACKET,
            12, 500,
            "center",
            "courier new")
        arcade.draw_text(
            f"To update a team member's level, type team id, comma, id, comma, new value and hit equal. "
            f"To delete a team member, type team id, comma, id and hit escape. ",
            140, 430,
            arcade.color.BLACK_LEATHER_JACKET,
            12, 500,
            "center",
            "courier new",
            multiline=True)
        arcade.draw_text(
            self.text,
            300, 350,
            arcade.color.BLACK_LEATHER_JACKET,
            20, 200,
            "center",
            "courier new")
        arcade.draw_text(
            f"{userName}, user no. {userId}",
            300, 50,
            arcade.color.BLACK_LEATHER_JACKET,
            12, 200,
            "center",
            "courier new")

        x = 0
        arcade.draw_text(f"team id : {userTeam.get('id')}", 100, 340, arcade.color.GENERIC_VIRIDIAN, 12)
        # print(f"user team {userTeam}")
        # print(f"user team items {userTeam.items()}")

        for pokemon in userTeam.items():
            if pokemon[0] == "id" :
                continue
            else :
                arcade.draw_text(f"{pokemon[1][0][0][0]} : {pokemon[1][0][0][1]}, item : {pokemon[1][1]}, level : {pokemon[1][2]}",
                                 100, 320 - (20 * x), arcade.color.GENERIC_VIRIDIAN, 12)
                x += 1

        x = 0
        arcade.draw_text(f"team id : {advTeam.get('id')}", 550, 340, arcade.color.ANTIQUE_RUBY, 12)
        for pokemon in advTeam.items():
            if pokemon[0] == "id" :
                continue
            else :
                arcade.draw_text(f"{pokemon[1][0][0][0]} : {pokemon[1][0][0][1]}, item : {pokemon[1][1]}, level : {pokemon[1][2]}",
                                 550, 320 - (20 * x), arcade.color.ANTIQUE_RUBY, 12)
                x += 1

        self.drawItemsList()
        self.drawBtns()
        self.manager.draw()

        arcade.finish_render()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER and len(USERPARTY) < 6:
            input = self.text.split(",")
            name = input[0].strip().title()
            item = input[1].strip().title()
            level = int(input[2].strip())
            self.loadPokemon(name)
            USERPARTY.append(self.pokemon[0])
            self.text = ''
            self.addToTeam(self.pokemon, userTeam.get("id"), item, level)
            userTeam[self.pokemon[0][0]] = (self.pokemon, item, level)

        elif key == arcade.key.TAB and len(ADVPARTY) < 6:
            input = self.text.split(",")
            name = input[0].strip().title()
            item = input[1].strip().title()
            level = int(input[2].strip())
            self.loadPokemon(name)
            ADVPARTY.append(self.pokemon[0])
            self.text = ''
            self.addToTeam(self.pokemon, advTeam.get("id"), item, level)
            advTeam[self.pokemon[0][0]] = (self.pokemon, item, level)

        elif key == arcade.key.LCTRL or key == arcade.key.RCTRL :
            global userName
            userName = self.text.strip().title()
            self.text = ''
            self.mySqlConnect()
            try :
                self.cur.callproc("createUser", [userName])
                self.conn.commit()
            except :
                self.conn.rollback()
                print("failed to create user")
            self.closeSqlConnection()

        # update team member
        elif key == arcade.key.EQUAL :
            input = self.text.split(",")
            tid = int(input[0].strip())
            pid = int(input[1].strip())
            newVal = int(input[2].strip())
            print(f"tid: {tid} pid: {pid}  newval: {newVal}")
            self.text = ''
            self.updateTeamMember(tid, pid, newVal)

        # delete team member
        elif key == arcade.key.ESCAPE :
            input = self.text.split(",")
            pid = int(input[1].strip())
            tid = int(input[0].strip())
            self.text = ''
            self.mySqlConnect()
            try:
                self.cur.callproc("deleteTeamMember", [pid, tid])
                self.conn.commit()
                if userTeam.get("id") == tid :
                    print(f"delete from {tid}")
                    userTeam.pop(pid)
                    index = 0
                    for u in USERPARTY :
                        if u[0] == pid :
                            index = USERPARTY.index(u)
                    USERPARTY.pop(index)
                else :
                    advTeam.pop(pid)
                    index = 0
                    for u in ADVPARTY:
                        if u[0] == pid:
                            index = ADVPARTY.index(u)
                    ADVPARTY.pop(index)
            except:
                self.conn.rollback()
                print(f"failed to delete {pid}")
            self.closeSqlConnection()

        # force move to next screen
        elif key == arcade.key.RIGHT :
            game_view = CompView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

        elif key == arcade.key.UP:
            game_view = InstructionsView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

        elif key == arcade.key.BACKSPACE:
            self.text = self.text[0: len(self.text) - 1]

        else:
            self.text += chr(key)

    def on_update(self, delta_time):
        if len(USERPARTY) == 6 and len(ADVPARTY) == 6:
            game_view = CompView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)
        if len(userName) > 0 :
            if len(userTeam.items()) == 0 :
                self.createDBTeams()

    def updateTeamMember(self, tid, pid, newVal):
        self.mySqlConnect()

        try :
            self.cur.callproc("updateTeamMember", [tid, pid, newVal])
            self.conn.commit()
            if userTeam.get("id") == tid:
                userTeam.update({pid[2]: newVal})
            else:
                advTeam.update({pid[2]: newVal})
            print(f"update tid {tid} pid {pid}, level to newval {newVal}")
        except :
            self.conn.rollback()
            print(f"failed to update {pid}")
            self.updateTeamMember(tid, pid, newVal)
        finally :
            self.closeSqlConnection()

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

        h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=20)
        menuBtn = arcade.gui.UIFlatButton(text="Menu", width=200, style=style1)
        nextBtn = arcade.gui.UIFlatButton(text="NEXT (right arrow)", width=200, style=style2)

        h_box.add(nextBtn)
        h_box.add(menuBtn)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_y=-200,
                child=h_box)
        )

        # handle clicks
        @menuBtn.event("on_click")
        def on_click_flatbutton(self, event):
            game_view = InstructionsView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

        @nextBtn.event("on_click")
        def on_click_flatbutton(self, event):
            print(event)
            game_view = CompView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

    def drawItemsList(self):
        self.mySqlConnect()
        self.cur.callproc("getItems", [])
        res = self.cur.fetchall()
        x = 0
        for row in res :
            arcade.draw_text(row[0], 15, 585 - x, arcade.color.BLACK_LEATHER_JACKET, 10, 100, "left", "courier new")
            x += 10

        self.closeSqlConnection()

    def loadPokemon(self, searchQry=None):
        self.mySqlConnect()

        if searchQry is not None:
            if searchQry.isnumeric():
                self.pid = int(searchQry)

                if self.pid in pokedex:
                    self.pokemon = pokedex.get(self.pid)
                else:
                    self.cur.callproc('findPokemonByID', [self.pid])
                    self.pokemon = self.cur.fetchall()
                    self.pid = self.pokemon[0][0]

                    self.cur.callproc('findPokemonPowersByID', [self.pid])
                    powers = self.cur.fetchall()
                    self.pokemon += powers

                    pokedex[self.pid] = self.pokemon
            else:
                self.cur.callproc('findPokemonByName', [searchQry])
                self.pokemon = self.cur.fetchall()
                self.pid = self.pokemon[0][0]

                self.cur.callproc('findPokemonPowersByID', [self.pid])
                powers = self.cur.fetchall()
                self.pokemon += powers

                pokedex[self.pid] = self.pokemon
        else:
            if self.pid in pokedex:
                self.pokemon = pokedex.get(self.pid)
            else:
                self.cur.callproc('findPokemonByID', [self.pid])
                self.pokemon = self.cur.fetchall()
                self.pid = self.pokemon[0][0]

                self.cur.callproc('findPokemonPowersByID', [self.pid])
                powers = self.cur.fetchall()
                self.pokemon += powers

                pokedex[self.pid] = self.pokemon

        self.closeSqlConnection()

    def createDBTeams(self):
        global userId, userName
        self.mySqlConnect()

        self.cur.callproc("getUserIDFromName", [userName])
        userId = self.cur.fetchall()[0][0]

        self.cur.callproc("getUserIDFromName", ["Adversary"])
        advId = self.cur.fetchall()[0][0]
        # print(f"advId {advId}")
        try :
            self.cur.callproc("createTeam", [userId])
            userTeam["id"] = self.cur.fetchall()[0][0]
            # print(f"user team id : {userTeam.get('id')}")
            self.conn.commit()
            print("created usr team")
        except :
            self.conn.rollback()
            print("failed to create usr team")

        try :
            self.cur.callproc("createTeam", [advId])
            temp = self.cur.fetchall()
            advTeam["id"] = temp[len(temp) - 1][0]
            # print(f"adv team id : {advTeam.get('id')}")
            self.conn.commit()
            print("created adv team")
        except :
            self.conn.rollback()
            print("failed to create adv team")

        try :
            self.cur.callproc("createBattle", [userTeam.get('id'), advTeam.get('id'), "Sinnoh"])
            self.conn.commit()
            print("created battle")
        except :
            self.conn.rollback()
            print("failed to create battle")

        self.closeSqlConnection()

    def addToTeam(self, pokemon, teamId, item, level):
        self.mySqlConnect()
        try :
            self.cur.callproc("addTeamMember", [pokemon[0][0], teamId, item, level])
            self.conn.commit()
            print(f"added {pokemon[0][0]} to team {teamId}")
        except :
            self.conn.rollback()
            print(f"failed to add {pokemon[0][0]} to team {teamId}")
        self.closeSqlConnection()

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
        self.pokemon = ((1, "Bulbasaur", 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
        self.text = ''
        self.pid = 1
        self.resp = ""
        self.respIsRec = False

    def on_show(self):
        arcade.set_background_color(arcade.color.ALMOND)
        self.manager.enable()

    def on_draw(self):
        arcade.start_render()
        self.manager.clear()
        self.drawBackground()
        self.establishWidgetSpace()
        # self.renderMenuButton(320, -250)
        self.manager.draw()
        arcade.finish_render()

    def on_hide_view(self):
        self.manager.disable()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.A :
            print("a clicked")
            self.mySqlConnect()
            self.cur.execute(f"select compareTeams({userTeam.get('id')}, {advTeam.get('id')});")
            self.resp = self.cur.fetchall()
            self.closeSqlConnection()
            self.respIsRec = False

        elif key == arcade.key.D :
            print("b clicked")
            self.mySqlConnect()
            print(userTeam.get('id'))
            self.cur.execute(f"select reccomendTeamMember({userTeam.get('id')});")
            self.resp = self.cur.fetchall()
            self.closeSqlConnection()
            self.respIsRec = True

        elif key == arcade.key.UP:
            game_view = InstructionsView(self.WIDTH, self.HEIGHT, self.sqlun, self.sqlpw)
            self.window.show_view(game_view)

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
        arcade.create_rectangle_filled(200, 415, 400, 370, arcade.color.LIGHT_CRIMSON, 0).draw()
        arcade.create_rectangle_filled(600, 415, 400, 370, arcade.color.LIGHT_MOSS_GREEN, 0).draw()
        # advs
        advs = list(advTeam.items())
        # print(advs)
        if len(advs) > 1 : arcade.draw_text(
            f"lvl {advs[1][1][2]} {advs[1][1][0][0][1]}, {advs[1][1][1]}",
            30, 428,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(advs) > 2 : arcade.draw_text(
            f"lvl {advs[2][1][2]} {advs[2][1][0][0][1]}, {advs[2][1][1]}",
            150, 428,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(advs) > 3 : arcade.draw_text(
            f"lvl {advs[3][1][2]} {advs[3][1][0][0][1]}, {advs[3][1][1]}",
            270, 428,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(advs) > 4 : arcade.draw_text(
            f"lvl {advs[4][1][2]} {advs[4][1][0][0][1]}, {advs[4][1][1]}",
            30, 270,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(advs) > 5 : arcade.draw_text(
            f"lvl {advs[5][1][2]} {advs[5][1][0][0][1]}, {advs[5][1][1]}",
            150, 270,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(advs) > 6 : arcade.draw_text(
            f"lvl {advs[6][1][2]} {advs[6][1][0][0][1]}, {advs[6][1][1]}",
            270, 270,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        # usrs
        usrs = list(userTeam.items())
        # print(usrs)
        if len(usrs) > 1 : arcade.draw_text(
            f"lvl {usrs[1][1][2]} {usrs[1][1][0][0][1]}, {usrs[1][1][1]}",
            430, 428,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(usrs) > 2 : arcade.draw_text(
            f"lvl {usrs[2][1][2]} {usrs[2][1][0][0][1]}, {usrs[2][1][1]}",
            550, 428,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(usrs) > 3 : arcade.draw_text(
            f"lvl {usrs[3][1][2]} {usrs[3][1][0][0][1]}, {usrs[3][1][1]}",
            670, 428,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(usrs) > 4 : arcade.draw_text(
            f"lvl {usrs[4][1][2]} {usrs[4][1][0][0][1]}, {usrs[4][1][1]}",
            430, 270,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(usrs) > 5 : arcade.draw_text(
            f"lvl {usrs[5][1][2]} {usrs[5][1][0][0][1]}, {usrs[5][1][1]}",
            550, 270,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")
        if len(usrs) > 6 : arcade.draw_text(
            f"lvl {usrs[6][1][2]} {usrs[6][1][0][0][1]}, {usrs[6][1][1]}",
            670, 270,
            arcade.color.BLACK_LEATHER_JACKET,
            10, 100,
            "center",
            "courier new")

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
            text="    Adversary Team",
            width=400,
            height=25,
            font_size=12,
            text_color=arcade.color.BLACK_LEATHER_JACKET,
            font_name="courier new")

        adversaryParty = arcade.gui.UIBoxLayout(x=0, y=230, space_between=25)
        rows = arcade.gui.UIBoxLayout(space_between=50)
        advTopRow = arcade.gui.UIBoxLayout(vertical=False, space_between=20)
        advBottomRow = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        if len(ADVPARTY) > 0:
            advSprite1 = self.renderPokemon(ADVPARTY[0][0])
        else:
            advSprite1 = arcade.Sprite()
        if len(ADVPARTY) > 1:
            advSprite2 = self.renderPokemon(ADVPARTY[1][0])
        else:
            advSprite2 = arcade.Sprite()
        if len(ADVPARTY) > 2:
            advSprite3 = self.renderPokemon(ADVPARTY[2][0])
        else:
            advSprite3 = arcade.Sprite()
        if len(ADVPARTY) > 3:
            advSprite4 = self.renderPokemon(ADVPARTY[3][0])
        else:
            advSprite4 = arcade.Sprite()
        if len(ADVPARTY) > 4:
            advSprite5 = self.renderPokemon(ADVPARTY[4][0])
        else:
            advSprite5 = arcade.Sprite()
        if len(ADVPARTY) > 5:
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

        rows.add(advTopRow)
        rows.add(arcade.gui.UIPadding(child=advBottomRow, padding=(0, 0, 50, 0)))
        adversaryParty.add(advPartyLabel)
        adversaryParty.add(rows)

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

        typeAdvBtn = arcade.gui.UIFlatButton(text="Compare Teams (click A)", width=170, height=60, style=style)
        bestAdtnBtn = arcade.gui.UIFlatButton(text="Recommend Addition (click D)", width=170, height=60, style=style)

        @typeAdvBtn.event("on_click")
        def on_click_flatbutton(event) :
            self.mySqlConnect()
            self.cur.execute(f"select compareTeams({userTeam.get('id')}, {advTeam.get('id')});")
            self.resp = self.cur.fetchall()
            self.closeSqlConnection()
            self.respIsRec = False

        @bestAdtnBtn.event("on_click")
        def on_click_flatbutton(event) :
            self.mySqlConnect()
            self.cur.execute(f"select reccomendTeamMember({userTeam.get('id')});")
            self.resp = self.cur.fetchall()
            self.closeSqlConnection()
            self.respIsRec = True

        calcBtnSpace = arcade.gui.UIPadding(
            child=arcade.gui.UIBoxLayout(
                space_between=20,
                vertical=False,
                children=(typeAdvBtn, bestAdtnBtn)),
            padding=(50, 20, 95, 20))

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

        userParty = arcade.gui.UIBoxLayout(x=400, y=230, space_between=25)
        rows = arcade.gui.UIBoxLayout(space_between=50)
        userTopRow = arcade.gui.UIBoxLayout(vertical=False, space_between=20)
        userBottomRow = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        if len(USERPARTY) > 0:
            userSprite1 = self.renderPokemon(USERPARTY[0][0])
        else:
            userSprite1 = arcade.Sprite()
        if len(USERPARTY) > 1:
            userSprite2 = self.renderPokemon(USERPARTY[1][0])
        else:
            userSprite2 = arcade.Sprite()
        if len(USERPARTY) > 2:
            userSprite3 = self.renderPokemon(USERPARTY[2][0])
        else:
            userSprite3 = arcade.Sprite()
        if len(USERPARTY) > 3:
            userSprite4 = self.renderPokemon(USERPARTY[3][0])
        else:
            userSprite4 = arcade.Sprite()
        if len(USERPARTY) > 4:
            userSprite5 = self.renderPokemon(USERPARTY[4][0])
        else:
            userSprite5 = arcade.Sprite()
        if len(USERPARTY) > 5:
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

        rows.add(userTopRow)
        rows.add(arcade.gui.UIPadding(child=userBottomRow, padding=(0, 0, 50, 0)))
        userParty.add(myTeamLabel)
        userParty.add(rows)

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

        if self.resp == "" :
            msg = ""
        else :
            if self.respIsRec :
                msg = f"Recommended party addition : {self.resp[0][0]}"
            else :
                msg = f"Where the user party is Team 1 and the adversary party is Team 2 : {self.resp[0][0]}"

        repsRes = arcade.gui.UITextArea(text=msg, width=300, height=205,
                                        text_color=arcade.color.BLACK_LEATHER_JACKET,
                                        font_name="courier new", multiline=True)

        reportsBox.add(reportsLabel)
        reportsBox.add(repsRes)

        return reportsBox

    def renderPokemon(self, pid):
        spritePath = pkg_resources.resource_filename("Pokedex", f"imgs/pokemon/{pid}.png")
        tex = arcade.load_texture(spritePath)
        spriteScale = self.WIDTH / (tex.width * 8)
        return arcade.Sprite(spritePath, spriteScale)

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
