from django.test import TestCase
from .models import ChessGame
from .chess_logic import process_move, create_initial_board
import json

class ChessGameTests(TestCase):

    def setUp(self):
        # Начальное состояние доски в виде JSON
        self.initial_board = create_initial_board()  # Предполагаем, что эта функция возвращает 2D список
        self.board_state = json.dumps(self.initial_board)  # Преобразуем его в JSON
        self.game = ChessGame.objects.create(turn='white', board_state=self.board_state)

    def test_valid_move_pawn(self):
        old_coords = (1, 0)  # Позиция пешки
        new_coords = (3, 0)  # Движение на две клетки впередЫ
        success, new_board = process_move(old_coords, new_coords, self.game.get_current_board())
        self.assertTrue(success)   # Ожидаем, что ход успешен

    def test_invalid_move(self):
        old_coords = (0, 0)  # Позиция ладьи
        new_coords = (1, 1)  # Неверное движение (ладья не может двигаться по диагонали)
        success, new_board = process_move(old_coords, new_coords, self.game.get_current_board())
        self.assertFalse(success)  # Ожидаем, что ход не успешен
