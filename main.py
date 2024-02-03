import tkinter as tk
from tkinter import messagebox

from zero import ZeroClient
from msgspec import Struct

zero_client = ZeroClient("localhost", 5559)

window = tk.Tk()
window.title("Tic Tac Toe")

# Create board
def create_board():
    for i in range(3):
        for j in range(3):
            button = tk.Button(window, text="", font=("Arial", 50), height=2, width=6, bg="lightblue", command=lambda row=i, col=j: handle_click(row, col))
            button.grid(row=i, column=j, sticky="nsew")

create_board()

# Initialize variables
board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
current_player = 1

# Handle button clicks
def handle_click(row, col):
    global current_player

    resp_dict = zero_client.call("click_board", dict(
        reset_board=board[row][col] == 0, column=col, row=row, current_player=current_player
    ))

    if board[row][col] == 0:
        board[row][col] = resp_dict.get('text')
        button = window.grid_slaves(row=resp_dict.get('row'), column=resp_dict.get('column'))[0]
        button.config(text=resp_dict.get('text'))

    current_player = resp_dict.get('current_player')

    check_for_winner()


# Check for a winner or a tie
def check_for_winner():
    winner = zero_client.call("check_board", dict(boardMatrix=board))

    if winner:
        declare_winner(winner)


# Declare the winner and ask to restart the game
def declare_winner(winner):
    message = zero_client.call("declare_winner", dict(winner=winner, notWinner=False))

    answer = messagebox.askyesno("Game Over", message + " Do you want to restart the game?")

    if answer:
        global board
        board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        for i in range(3):
            for j in range(3):
                button = window.grid_slaves(row=i, column=j)[0]
                button.config(text="")

        global current_player
        current_player = 1
    else:
        window.quit()

window.mainloop()
