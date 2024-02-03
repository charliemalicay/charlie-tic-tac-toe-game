from zero import ZeroServer
from msgspec import Struct

from dataclasses import dataclass

from datetime import datetime

import msgpack


@dataclass
class Btype:
    def pack(self):
        return msgpack.packb(Btype.get_all_vars(self))

    @classmethod
    def unpack(cls, d):
        return cls(**msgpack.unpackb(d, raw=False))

    @staticmethod
    def get_all_vars(obj):
        values = vars(obj)
        for k, v in values.items():
            if isinstance(v, Btype):
                values[k] = vars(v)
        return values


app = ZeroServer(port=5559)


@dataclass
class BoardDataRequest(Btype):
    reset_board: bool
    column: int
    row: int
    current_player: int


@dataclass
class CheckBoardRequest(Btype):
    boardMatrix: list


@dataclass
class DeclareWinnerRequest(Btype):
    winner: list
    notWinner: bool


@dataclass
class BoardResponse(Btype):
    text: str
    column: int
    row: int
    current_player: int


@app.register_rpc
def click_board(args: dict) -> dict:
    req = BoardDataRequest(**args)

    text = 'O'

    reset_board = req.reset_board
    column = req.column
    row = req.row
    current_player = req.current_player

    if reset_board:
        if current_player == 1:
            text = "X"
            current_player = 2
        else:
            current_player = 1

    resp = BoardResponse(text, column, row, current_player)

    return resp.__dict__


@app.register_rpc
def check_board(args: dict) -> int:
    req = CheckBoardRequest(**args)

    winner = None
    board = req.boardMatrix

    # Check rows
    for row in board:
        if row.count(row[0]) == len(row) and row[0] != 0:
            winner = row[0]
            break

    # Check columns
    for col in range(len(board)):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != 0:
            winner = board[0][col]
            break

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != 0:
        winner = board[0][0]

    elif board[0][2] == board[1][1] == board[2][0] and board[0][2] != 0:
        winner = board[0][2]

    if all([all(row) for row in board]) and winner is None:
        winner = "tie"

    return winner


@app.register_rpc
def declare_winner(args: dict) -> str:
    req = DeclareWinnerRequest(**args)
    message = ""

    winner = req.winner
    not_winner = req.notWinner

    if winner == "tie":
        message = "It's a tie!"
    elif (winner == 'X' and not not_winner) or (winner == 'O' and not_winner):
        message = f"Player X wins!"
    elif (winner == 'O' and not not_winner) or (winner == 'X' and not_winner):
        message = f"Player O wins!"

    return message


if __name__ == "__main__":
    app.run()
