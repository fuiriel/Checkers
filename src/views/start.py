from src.views.view import View
from src.views.widgets import *


# Widok startowy
class StartView(View):

    def __init__(self, app_ref):
        super().__init__(app_ref)
        self.player = tk.StringVar()
        self.players = Select(self, self.player, *PLAYERS)
        self.players['width'] = 20
        self.players.config(font=gen_font(12), width=19)
        self.players_label = Label(self, 'Start player:')

        self.max_depth = tk.IntVar()
        self.number_box = NumberBox(self, self.max_depth)
        self.number_box.config(width=20)
        self.textbox_label = Label(self, 'Max search depth:')
        self.max_depth.trace('w', lambda name, index, mode, value=self.max_depth: self.on_depth_change(value.get()))

        self.start_game_btn = Button(self, text='Start game')
        self.start_game_btn['command'] = self.start_game
        self.start_game_btn['state'] = tk.DISABLED

    def display_view(self):
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        self.players_label.grid(column=0, row=1)
        self.players.grid(column=0, row=2)
        self.textbox_label.grid(column=0, row=3)
        self.number_box.grid(column=0, row=4)
        self.start_game_btn.grid(column=0, row=5, pady=40)

    def on_depth_change(self, value):
        self.start_game_btn['state'] = tk.DISABLED if not value else tk.NORMAL

    def start_game(self):
        max_depth = self.max_depth.get()
        player = self.player.get()
        print(player, max_depth)

        if max_depth and player:
            self.app_ref.change_view(ViewType.GAME)

