from django.db import models
import json
class Piece:
    def __init__(self, piece_type, color):
        self.type = piece_type
        self.color = color

    def to_dict(self):
        return {'type': self.type, 'color': self.color}

class ChessGame(models.Model):
    board_state = models.TextField()  # Состояние доски в виде JSON
    turn = models.CharField(max_length=5)  # 'white' или 'black'
    move_history = models.TextField(default="[]")  # История ходов в формате JSON

    def get_current_board(self): #получает текущее состояние доски
        board_state_str = self.board_state
        if not board_state_str:
            return [[None for _ in range(8)] for _ in range(8)]  # Инициализация пустой доски

        board_data = json.loads(board_state_str)
        board = []
        for row in board_data:
            board_row = []
            for piece_data in row:
                if piece_data:
                    color = piece_data.get("color")
                    type = piece_data.get("type")
                    piece = Piece(type, color)
                    board_row.append(piece)
                else:
                    board_row.append(None)
            board.append(board_row)
        return board

    def update_board(self, new_board):
        serialized_board = []
        for row in new_board:
            serialized_row = []
            for piece in row:
                if piece:
                    serialized_row.append(piece.to_dict())  # Сериализация фигуры в словарь
                else:
                    serialized_row.append(None)
            serialized_board.append(serialized_row)

        self.board_state = json.dumps(serialized_board)
        self.save()
