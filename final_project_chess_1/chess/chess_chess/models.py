from django.db import models
from django.core.exceptions import ValidationError
from .chess_logic import ChessBoard
# Create your models here.
class ChessGame(models.Model):
    WHITE = 'white'
    BLACK = 'black'
    TURN_CHOICES = [
        (WHITE, 'White'),
        (BLACK, 'Black'),
    ]

    turn = models.CharField(max_length=5, choices=TURN_CHOICES, default=WHITE)
    board = models.JSONField(default=dict)

    def __str__(self):
        return f"Game {self.id}: Turn: {self.turn}"

    def create_board(self):
        self.board = {
            (0, 0): {'type': 'Rook', 'color': self.BLACK},
            (1, 0): {'type': 'Knight', 'color': self.BLACK},
            (2, 0): {'type': 'Bishop', 'color': self.BLACK},
            (3, 0): {'type': 'Queen', 'color': self.BLACK},
            (4, 0): {'type': 'King', 'color': self.BLACK},
            (5, 0): {'type': 'Bishop', 'color': self.BLACK},
            (6, 0): {'type': 'Knight', 'color': self.BLACK},
            (7, 0): {'type': 'Rook', 'color': self.BLACK},
            (0, 1): {'type': 'Pawn', 'color': self.BLACK},
            (1, 1): {'type': 'Pawn', 'color': self.BLACK},
            (2, 1): {'type': 'Pawn', 'color': self.BLACK},
            (3, 1): {'type': 'Pawn', 'color': self.BLACK},
            (4, 1): {'type': 'Pawn', 'color': self.BLACK},
            (5, 1): {'type': 'Pawn', 'color': self.BLACK},
            (6, 1): {'type': 'Pawn', 'color': self.BLACK},
            (7, 1): {'type': 'Pawn', 'color': self.BLACK},
            (0, 7): {'type': 'Rook', 'color': self.WHITE},
            (1, 7): {'type': 'Knight', 'color': self.WHITE},
            (2, 7): {'type': 'Bishop', 'color': self.WHITE},
            (3, 7): {'type': 'Queen', 'color': self.WHITE},
            (4, 7): {'type': 'King', 'color': self.WHITE},
            (5, 7): {'type': 'Bishop', 'color': self.WHITE},
            (6, 7): {'type': 'Knight', 'color': self.WHITE},
            (7, 7): {'type': 'Rook', 'color': self.WHITE},
            (0, 6): {'type': 'Pawn', 'color': self.WHITE},
            (1, 6): {'type': 'Pawn', 'color': self.WHITE},
            (2, 6): {'type': 'Pawn', 'color': self.WHITE},
            (3, 6): {'type': 'Pawn', 'color': self.WHITE},
            (4, 6): {'type': 'Pawn', 'color': self.WHITE},
            (5, 6): {'type': 'Pawn', 'color': self.WHITE},
            (6, 6): {'type': 'Pawn', 'color': self.WHITE},
            (7, 6): {'type': 'Pawn', 'color': self.WHITE},
        }
        self.save()

    def move_piece(self, start_position, new_position):
        """Перемещение фигуры, если ход допустим."""
        print(f"Attempting to move from {start_position} to {new_position}")
        piece = self.board.get(tuple(start_position))
        board_instance = ChessBoard()  # Создаем объект класса ChessBoard

        if piece:
            print(f"Piece found: {piece} at {start_position}")  # Проверяем, что фигура найдена
            if new_position in piece.valid_moves(start_position, board_instance):
                # Если перемещение допустимо, перемещаем фигуру
                self.board[tuple(new_position)] = piece
                del self.board[tuple(start_position)]
                self.turn = self.BLACK if self.turn == self.WHITE else self.WHITE
                self.save()
                print(f"Moved piece to {new_position}, new turn: {self.turn}")
                return True

        print("No piece found at starting position or invalid move.")
        raise ValidationError("Invalid move.")

class ChessPiece:
    def __init__(self, color, type):
        self.color = color
        self.type = type

    def valid_moves(self, start_position, board):
        # Этот метод должен быть переопределен для каждого типа фигуры
        raise NotImplementedError


class Pawn(ChessPiece):
    def valid_moves(self, start_position, board):
        # Логика для пешек
        moves = []
        direction = 1 if self.color == 'white' else -1

        # Стандартный ход на одну клетку вперед
        forward_move = (start_position[0], start_position[1] + direction)
        if board.is_empty(forward_move):
            moves.append(forward_move)

        # Возможный ход на две клетки вперед
        if (self.color == 'white' and start_position[1] == 1) or (self.color == 'black' and start_position[1] == 6):
            double_move = (start_position[0], start_position[1] + 2 * direction)
            if board.is_empty(double_move):
                moves.append(double_move)

        # Ход с захватом
        capture_moves = [
            (start_position[0] - 1, start_position[1] + direction),  # Влево на одну клетку
            (start_position[0] + 1, start_position[1] + direction)   # Вправо на одну клетку
        ]
        for capture in capture_moves:
            if board.is_occupied_by_enemy(capture, self.color):
                moves.append(capture)
        print(f"Valid moves for pawn: {moves}")
        return moves


class Rook(ChessPiece):
    def valid_moves(self, start_position, board):
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Вверх, вправо, вниз, влево

        for direction in directions:
            for step in range(1, 8):
                new_position = (start_position[0] + direction[0] * step, start_position[1] + direction[1] * step)
                if board.is_within_bounds(new_position):
                    if board.is_empty(new_position):
                        moves.append(new_position)
                    elif board.is_occupied_by_enemy(new_position, self.color):
                        moves.append(new_position)
                        break  # Убили, не можем продолжать
                    else:
                        break  # Своя фигура, останавливаемся
                else:
                    break  # Выходим за пределы доски

        return moves

class Bishop(ChessPiece):
    def valid_moves(self, start_position, board):
        # Логика для слона
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Все 4 диагонали

        for direction in directions:
            for step in range(1, 8):
                new_position = (start_position[0] + direction[0] * step, start_position[1] + direction[1] * step)
                if board.is_within_bounds(new_position):
                    if board.is_empty(new_position):
                        moves.append(new_position)
                    elif board.is_occupied_by_enemy(new_position, self.color):
                        moves.append(new_position)
                        break
                    else:
                        break
                else:
                    break

        return moves


class ChessBoard:
    def __init__(self):
        self.board = self.create_board()




    def is_empty(self, position):
        x, y = position
        return self.board[x][y] is None

    def is_occupied_by_enemy(self, position, color):
        x, y = position
        piece = self.board[x][y]
        return piece is not None and piece.color != color

    def is_within_bounds(self, position):
        x, y = position
        return 0 <= x < 8 and 0 <= y < 8

