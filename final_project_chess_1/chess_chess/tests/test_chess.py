import unittest
from chess_logic import (
    is_valid_move,
    move_pawn,
    move_rook,
    move_knight,
    move_bishop,
    move_queen,
    process_move,
    create_initial_board
)

class TestChessMoves(unittest.TestCase):

    def setUp(self):
        self.board = create_initial_board()

    def test_is_valid_move(self):
        # Тест для допустимого перемещения
        self.assertTrue(is_valid_move('P', (6, 1), (5, 1), self.board))  # белая пешка вперед
        self.assertTrue(is_valid_move('P', (6, 1), (5, 2), self.board))  # белая пешка по диагонали без врага
        self.assertTrue(is_valid_move('p', (1, 1), (3, 1), self.board))  # черная пешка (перемещение вниз)
        self.assertTrue(is_valid_move('R', (0, 0), (0, 5), self.board))  # белая ладья

    def test_move_pawn(self):
        result = move_pawn((6, 1), (5, 1), self.board)
        self.assertEqual(result[0], True)  # ожидаем, что перемещение успешно
        self.assertIsNone(self.board[6][1])  # старая позиция должна быть пустой
        self.assertEqual(self.board[5][1], 'P')  # новая позиция должна содержать пешку

        result = move_pawn((6, 2), (4, 2), self.board)  # Двойной ход
        self.assertEqual(result[0], True)  # ожидаем, что перемещение успешно

    def test_move_rook(self):
        self.board[0][0] = 'r'  # Помещаем белую ладью на (0, 0)
        result = move_rook((0, 0), (0, 2), self.board)
        self.assertEqual(result[0], False)  # перемещение по горизонтали
        # self.assertIsNone(self.board[0][0])  # старая позиция должна быть пустой
        # self.assertEqual(self.board[0][4], 'R')  # новая позиция должна содержать ладью
        #
        # result = move_rook((0, 4), (1, 4), self.board)  # вертикальный ход
        # self.assertEqual(result[0], False)  # перемещение не должно быть успешным

    def test_move_knight(self):
        self.board[0][1] = 'N'  # Помещаем коня на (0, 1)
        result = move_knight((0, 1), (2, 2), self.board)
        self.assertEqual(result[0], True)  # допустимое движение конем

        result = move_knight((2, 2), (3, 3), self.board)
        self.assertEqual(result[0], False)  # недопустимое движение

    # def test_move_bishop(self):
    #     self.board[0][2] = 'B'  # Помещаем слона на (0, 2)
    #     result = move_bishop((0, 2), (2, 4), self.board)
    #     self.assertEqual(result[0], True)  # допустимое движение по диагонали
    #
    #     result = move_bishop((2, 4), (3, 4), self.board)
    #     self.assertEqual(result[0], False)  # недопустимое движение
    #
    # def test_move_queen(self):
    #     self.board[0][3] = 'Q'  # Помещаем ферзя на (0, 3)
    #     result = move_queen((0, 3), (0, 5), self.board)
    #     self.assertEqual(result[0], True)  # допустимое горизонтальное движение
    #
    #     result = move_queen((0, 3), (1, 4), self.board)
    #     self.assertEqual(result[0], False)  # недопустимое движение

if __name__ == '__main__':
    unittest.main()
