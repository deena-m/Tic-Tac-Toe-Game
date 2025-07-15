import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple


class Player(NamedTuple):
    label: str
    color: str


class Move(NamedTuple):
    row: int
    col: int
    label: str = ""


BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="red"),
    Player(label="O", color="blue"),
)


class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._has_winner = False
        self._setup_board()

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [[(move.row, move.col) for move in row] for row in self._current_moves]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def is_valid_move(self, move):
        return not self._has_winner and self._current_moves[move.row][move.col].label == ""

    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(self._current_moves[n][m].label for n, m in combo)
            if len(results) == 1 and "" not in results:
                self._has_winner = True
                self.winner_combo = combo
                break

    def has_winner(self):
        return self._has_winner

    def is_tied(self):
        return not self._has_winner and all(move.label for row in self._current_moves for move in row)

    def toggle_player(self):
        self.current_player = next(self._players)

    def reset_game(self):
        self._setup_board()
        self._has_winner = False
        self.winner_combo = []


class TicTacToeBoard(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Tic-Tac-Toe by Deena")
        self._cells = {}
        self._game = game
        self.time_left = 20  # Timer set to 20 seconds
        self.timer_running = False

        self._create_menu()
        self._create_board_display()
        self._create_board_grid()
        self.start_timer()  # Start timer at game start

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Play Again", command=self.reset_board)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)

        self.display = tk.Label(master=display_frame, text="Ready?", font=font.Font(size=28, weight="bold"))
        self.display.pack()

        self.timer_label = tk.Label(
            master=display_frame,
            text=f"Time Left: {self.time_left} sec",
            font=font.Font(size=14, weight="bold"),
            fg="white"
        )
        self.timer_label.pack()

        # 🔹 "Reset Game" Button
        self.reset_button = tk.Button(
            master=display_frame,
            text="Reset Game",
            font=font.Font(size=12, weight="bold"),
            command=self.reset_board,
            bg="lightgray",
            fg="black"
        )
        self.reset_button.pack(pady=5)

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(family="comic sans MS", size=56, weight="bold"),
                    fg="black",
                    width=2,
                    height=1,
                    highlightbackground="lightpink",
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def start_timer(self):
        """Starts the timer with a slower speed."""
        self.time_left = 15  # Reset timer to 15 sec
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        """Updates the timer every 1.5 seconds instead of 1 second to slow it down."""
        if self._game.has_winner():  # Stop timer if game is won
            self.timer_running = False
            return

        if self.time_left > 0:
            self.timer_label.config(text=f"Time Left: {self.time_left} sec")
            self.time_left -= 1
            self.after(1500, self.update_timer)  # Slower countdown (1.5 sec instead of 1 sec)
        else:
            self.timer_running = False
            self._update_display(msg=f"{self._game.current_player.label} ran out of time!", color="red")
            self._game.toggle_player()
            self.start_timer()

    def _highlight_cells(self):
        """Highlights the winning cells when a player wins."""
        for button, (row, col) in self._cells.items():
            if (row, col) in self._game.winner_combo:
                button.config(bg="yellow")

    def play(self, event):
        if not self.timer_running:
            return

        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = Move(row, col, self._game.current_player.label)

        if self._game.is_valid_move(move):
            self._update_button(clicked_btn)
            self._game.process_move(move)

            if self._game.has_winner():
                self._highlight_cells()  # Highlight winning move
                self._update_display(msg=f'Player "{self._game.current_player.label}" won!',
                                     color=self._game.current_player.color)
                self.timer_running = False  # Stop the timer when someone wins
            elif self._game.is_tied():
                self._update_display(msg="Tied game!", color="red")
                self.timer_running = False
            else:
                self._game.toggle_player()
                self.start_timer()
                self._update_display(f"{self._game.current_player.label}'s turn")

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    def _update_display(self, msg, color="black"):
        self.display.config(text=msg, fg=color)

    def reset_board(self):
        self._game.reset_game()
        self._update_display(msg="Ready?")
        self.timer_running = False
        self.timer_label.config(text="Time Left: 15 sec")

        for button in self._cells.keys():
            button.config(highlightbackground="skyblue", text="", fg="black", bg="SystemButtonFace")

        self.start_timer()


def main():
    game = TicTacToeGame()
    board = TicTacToeBoard(game)
    board.mainloop()


if __name__ == "__main__":
    main()
