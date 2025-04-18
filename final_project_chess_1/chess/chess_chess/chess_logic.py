# chess/chess_logic.py
class ChessPiece:
    def __init__(self, color):
        self.color = color

    def valid_moves(self, start_position, board):
        raise NotImplementedError


class Pawn(ChessPiece):
    def valid_moves(self, start_position, board):
        moves = []
        direction = 1 if self.color == 'white' else -1
        print(f"Validating moves for pawn at {start_position}")

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
            (start_position[0] + 1, start_position[1] + direction)  # Вправо на одну клетку
        ]
        for capture in capture_moves:
            if board.is_occupied_by_enemy(capture, self.color):
                moves.append(capture)

        print(f"Valid moves for pawn: {moves}")
        return moves

    def promote(self):
        # Превращение пешки в ферзя, слона, коня или ладью
        return Queen(self.color)  # По умолчанию превращаем в ферзя

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


class Knight(ChessPiece):
    def valid_moves(self, start_position, board):
        moves = []
        x, y = start_position
        # Все возможные ходы коня
        potential_moves = [
            (x + 2, y + 1), (x + 2, y - 1),
            (x - 2, y + 1), (x - 2, y - 1),
            (x + 1, y + 2), (x + 1, y - 2),
            (x - 1, y + 2), (x - 1, y - 2)
        ]

        for move in potential_moves:
            if board.is_within_bounds(move) and (board.is_empty(move) or board.is_occupied_by_enemy(move, self.color)):
                moves.append(move)

        return moves

class Bishop(ChessPiece):
    def valid_moves(self, start_position, board):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # По диагоналям

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

class Queen(ChessPiece):
    def valid_moves(self, start_position, board):
        moves = []
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # Вверх, вправо, вниз, влево
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # По диагоналям
        ]

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


class King(ChessPiece):
    def valid_moves(self, start_position, board):
        moves = []
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # Вверх, вправо, вниз, влево
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # По диагоналям
        ]

        for direction in directions:
            new_position = (start_position[0] + direction[0], start_position[1] + direction[1])
            if board.is_within_bounds(new_position):
                if board.is_empty(new_position) or board.is_occupied_by_enemy(new_position, self.color):
                    moves.append(new_position)  # Легальный ход, даже если захват

        return moves


class ChessBoard:
    def __init__(self):
        self.board = self.create_board()
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False

    def create_board(self):
        # Создание и инициализация доски с фигурами
        board = [[None for _ in range(8)] for _ in range(8)]
        # Пример: инициализация фигур
        for x in range(8):
            board[x][1] = Pawn('black')
            board[x][6] = Pawn('white')
        board[0][0] = Rook('black')
        board[0][7] = Rook('white')
        board[1][0] = Knight('black')
        board[1][7] = Knight('white')
        board[2][0] = Bishop('black')
        board[2][7] = Bishop('white')
        board[3][0] = Queen('black')
        board[3][7] = Queen('white')
        board[4][0] = King('black')
        board[4][7] = King('white')
        board[5][0] = Bishop('black')
        board[5][7] = Bishop('white')
        board[6][0] = Knight('black')
        board[6][7] = Knight('white')
        board[7][0] = Rook('black')
        board[7][7] = Rook('white')
        return board

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

    def perform_castle(self, king_pos, rook_pos):
        king = self.board[king_pos[0]][king_pos[1]]
        rook = self.board[rook_pos[0]][rook_pos[1]]

        # Выполнение рокировки
        if king and isinstance(king, King) and rook and isinstance(rook, Rook):
            if self.white_king_moved or self.white_rook_h_moved:
                return False  # Для белых короля и ладьи
            if self.is_empty((king_pos[0], king_pos[1] - 1)) and self.is_empty((king_pos[0], king_pos[1] - 2)):
                self.board[king_pos[0]][king_pos[1] - 1] = rook
                self.board[rook_pos[0]][rook_pos[1]] = None
                self.board[king_pos[0]][king_pos[1]] = None
                self.board[king_pos[0]][king_pos[1] - 1] = king
                return True
            return False

    def is_in_check(self, color):
        king_position = self.find_king(color)

        if not king_position:
            return False  # Король не найден

        # Проверяем все атакующие фигуры
        for x in range(8):
            for y in range(8):
                piece = self.board[x][y]
                if piece and piece.color != color:
                    if king_position in piece.valid_moves((x, y), self):
                        return True  # Король под угрозой
        return False

    def find_king(self, color):
        for x in range(8):
            for y in range(8):
                piece = self.board[x][y]
                if isinstance(piece, King) and piece.color == color:
                    return (x, y)
        return None

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False  # Если не в шаху, не может быть мата

        # Проверяем все легальные ходы для всех фигур
        for x in range(8):
            for y in range(8):
                piece = self.board[x][y]
                if piece and piece.color == color:
                    valid_moves = piece.valid_moves((x, y), self)
                    for move in valid_moves:
                        original_position = (x, y)
                        target_piece = self.board[move[0]][move[1]]
                        # Пробуем сделать ход
                        self.board[move[0]][move[1]] = piece
                        self.board[x][y] = None
                        if not self.is_in_check(color):
                            # Вернуть обратно
                            self.board[x][y] = piece
                            self.board[move[0]][move[1]] = target_piece
                            return False  # Легальный ход найден
        return True  # Нет легальных ходов, это мат
