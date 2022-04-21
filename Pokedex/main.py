#!/usr/bin/python3

import sys
import arcade
import arcade.gui
import pkg_resources
import pymysql

from pokemon import Pokemon

WIDTH = 800
HEIGHT = 600
TITLE = "Pokédex 2: the SQL"
pokedex = dict()


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
        self.drawBackground()
        self.establishWidgetSpace()
        self.renderMenuButton(250, 250)
        self.manager.draw()
        arcade.finish_render()

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
        arcade.create_rectangle_filled(200, 450, 400, 300, arcade.color.BARN_RED, 0).draw()

        arcade.create_rectangle_filled(85, 485, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(200, 485, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(315, 485, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(85, 370, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(200, 370, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(315, 370, 100, 100, arcade.color.WHITE, 0).draw()

        # calcBG
        arcade.create_rectangle_filled(200, 150, 400, 300, arcade.color.ALMOND, 0).draw()

        # reportsBG
        arcade.create_rectangle_filled(600, 450, 400, 300, arcade.color.ALMOND, 0).draw()

        # usrBG
        arcade.create_rectangle_filled(600, 150, 400, 300, arcade.color.GENERIC_VIRIDIAN, 0).draw()

        arcade.create_rectangle_filled(480, 70, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(600, 70, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(720, 70, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(480, 190, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(600, 190, 100, 100, arcade.color.WHITE, 0).draw()
        arcade.create_rectangle_filled(720, 190, 100, 100, arcade.color.WHITE, 0).draw()

    def establishWidgetSpace(self):
        # whole screen : left and right
        h_box = arcade.gui.UIBoxLayout(vertical=False)
        left_box = arcade.gui.UIBoxLayout()
        right_box = arcade.gui.UIBoxLayout()

        # top left widget : adversary party
        adversaryParty = arcade.gui.UIBoxLayout(space_between=20)
        advPartyLabel = arcade.gui.UITextArea(#x=200,
                                              #y=555,
                                              text="Adversary Party",
                                              width=400,
                                              height=45,
                                              font_size=12,
                                              text_color=arcade.color.WHITE,
                                              font_name="courier new")
        advTopRow = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        advBottomRow = arcade.gui.UIBoxLayout(vertical=False, space_between=15)

        adv1 = arcade.gui.UIInteractiveWidget()
        adv2 = arcade.gui.UIInteractiveWidget()
        adv3 = arcade.gui.UIInteractiveWidget()
        adv4 = arcade.gui.UIInteractiveWidget()
        adv5 = arcade.gui.UIInteractiveWidget()
        adv6 = arcade.gui.UIInteractiveWidget()

        adv1.on_click = self.onClickAdjustParty
        adv2.on_click = self.onClickAdjustParty
        adv3.on_click = self.onClickAdjustParty
        adv4.on_click = self.onClickAdjustParty
        adv5.on_click = self.onClickAdjustParty
        adv6.on_click = self.onClickAdjustParty

        adv1Border = arcade.gui.UIBorder(child=adv1)
        adv2Border = arcade.gui.UIBorder(child=adv2)
        adv3Border = arcade.gui.UIBorder(child=adv3)
        adv4Border = arcade.gui.UIBorder(child=adv4)
        adv5Border = arcade.gui.UIBorder(child=adv5)
        adv6Border = arcade.gui.UIBorder(child=adv6)

        advTopRow.add(adv1Border)
        advTopRow.add(adv2Border)
        advTopRow.add(adv3Border)
        advBottomRow.add(adv4Border)
        advBottomRow.add(adv5Border)
        advBottomRow.add(adv6Border)

        adversaryParty.add(advPartyLabel)
        adversaryParty.add(advTopRow)
        adversaryParty.add(advBottomRow)

        adversaryPartyBorder = arcade.gui.UIBorder(child=adversaryParty)

        # bottom left widget : calculations buttons
        calcBox = arcade.gui.UIInteractiveWidget(x=0, y=0, width=400, height=300)
        calcLabel = arcade.gui.UITextArea(text="Calculations: ",
                                          width=400,
                                          height=20,
                                          font_size=12,
                                          text_color=arcade.color.BLACK,
                                          font_name="courier new")
        calcBox.add(calcLabel)
        calcBoxBorder = arcade.gui.UIBorder(child=calcBox)

        # add to parent widget
        left_box.add(adversaryPartyBorder)
        left_box.add(calcBoxBorder)

        # top right widget : generated reports
        # TODO : text = sql procedure to get calc results
        reportsBox = arcade.gui.UISpace(width=400,
                                        height=300)
        text = "Reports: "
        reports = arcade.gui.UITextArea(#x=400,
                                        #y=450,
                                        text=text,
                                        font_size=12,
                                        text_color=arcade.color.BLACK,
                                        font_name="courier new")
        reportsBox.add(reports)
        reportsBoxBorder = arcade.gui.UIBorder(child=reportsBox)

        # bottom right widget : user party
        myTeamLabel = arcade.gui.UILabel(text="My Team",
                                         width=400,
                                         height=20,
                                         font_size=12,
                                         font_name="courier new")
        userParty = arcade.gui.UIBoxLayout(space_between=20)
        userTopRow = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        userBottomRow = arcade.gui.UIBoxLayout(vertical=False, space_between=15)

        user1 = arcade.gui.UIInteractiveWidget()
        user2 = arcade.gui.UIInteractiveWidget()
        user3 = arcade.gui.UIInteractiveWidget()
        user4 = arcade.gui.UIInteractiveWidget()
        user5 = arcade.gui.UIInteractiveWidget()
        user6 = arcade.gui.UIInteractiveWidget()
        """

        user1.on_click = self.onClickAdjustParty
        user2.on_click = self.onClickAdjustParty
        user3.on_click = self.onClickAdjustParty
        user4.on_click = self.onClickAdjustParty
        user5.on_click = self.onClickAdjustParty
        user6.on_click = self.onClickAdjustParty
        """

        user1Border = arcade.gui.UIBorder(child=user1)
        user2Border = arcade.gui.UIBorder(child=user2)
        user3Border = arcade.gui.UIBorder(child=user3)
        user4Border = arcade.gui.UIBorder(child=user4)
        user5Border = arcade.gui.UIBorder(child=user5)
        user6Border = arcade.gui.UIBorder(child=user6)

        userTopRow.add(user1Border)
        userTopRow.add(user2Border)
        userTopRow.add(user3Border)
        userBottomRow.add(user4Border)
        userBottomRow.add(user5Border)
        userBottomRow.add(user6Border)

        userParty.add(myTeamLabel)
        userParty.add(userTopRow)
        userParty.add(userBottomRow)

        userPartyBorder = arcade.gui.UIBorder(child=userParty)

        # add to parent widgets
        right_box.add(reportsBoxBorder)
        right_box.add(userPartyBorder)

        h_box.add(left_box)
        h_box.add(right_box)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=h_box)
        )

    def onClickAdjustParty(self, event):
        # The code in this function is run when we click the ok button.
        # The code below opens the message box and auto-dismisses it when done.
        message_box = arcade.gui.UIMessageBox(
            width=300,
            height=200,
            message_text=(
                "Add party member : "
            ),
            callback=self.on_message_box_close,
            buttons=["Ok", "Cancel"]
        )

        self.manager.add(message_box)

    def on_message_box_close(self, button_text):
        print(f"User pressed {button_text}.")


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
