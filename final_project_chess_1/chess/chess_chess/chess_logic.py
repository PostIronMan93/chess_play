def is_valid_move(figure, old_coords, new_coords, board):
    print(f"Checking move for {figure} from {old_coords} to {new_coords}")
    # Проверяем, что новые координаты находятся в пределах доски
    if not (0 <= new_coords[0] < 8 and 0 <= new_coords[1] < 8):
        print("Move out of bounds")
        return False
    if old_coords == new_coords:
        print("Move to the same position")
        return False
    # Проверяем, что фигура не движется на свою позицию
    target = board[new_coords[0]][new_coords[1]]
    if target is not None and target.islower() == figure.islower():  # проверяем цвет
        print("Cannot move to a square occupied by own piece")
        return False
    return True
def move_pawn(old_coords, new_coords, board):
    # Логика движения для пешки
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]

    if figure is None:
        return (False, board)
    # Определяем направление движения
    direction = 1 if figure.islower() else -1

    # Простое движение вперед
    if new_x == old_x + direction and new_y == old_y and board[new_x][new_y] is None:
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)

    # Возможность двойного хода с начальной позиции
    if (old_x == 6 and figure.isupper() and new_x == 4 and new_y == old_y and board[5][old_y] is None and board[4][old_y] is None) or \
       (old_x == 1 and figure.islower() and new_x == 3 and new_y == old_y and board[2][old_y] is None and board[3][old_y] is None):
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)

    # Удар по диагонали
    if new_x == old_x + direction and abs(new_y - old_y) == 1 and board[new_x][new_y] is not None:
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)

    return (False, board)
def move_rook(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]

    if figure is None:
        return (False, board)

    # Проверка перемещения по вертикали или горизонтали
    if old_x != new_x and old_y != new_y:
        return (False, board)

    # Проверка на наличие других фигур на пути
    step_x = (new_x - old_x) // max(1, abs(new_x - old_x)) if old_x != new_x else 0
    step_y = (new_y - old_y) // max(1, abs(new_y - old_y)) if old_y != new_y else 0

    # Перемещение по пути
    x, y = old_x + step_x, old_y + step_y
    while (x, y) != (new_x, new_y):
        if board[x][y] is not None:
            return (False, board)
        x += step_x
        y += step_y

    # Перемещение
    board[new_x][new_y] = figure
    board[old_x][old_y] = None
    return (True, board)


def move_knight(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]

    if figure is None:
        return (False, board)

    # Определяем допустимое движение конем
    if (abs(new_x - old_x), abs(new_y - old_y)) in [(2, 1), (1, 2)]:
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)
    return (False, board)
def move_bishop(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]

    if figure is None:
        return (False, board)

    # Проверяем, что перемещение по диагонали
    if abs(new_x - old_x) != abs(new_y - old_y):
        return (False, board)

    step_x = 1 if new_x > old_x else -1
    step_y = 1 if new_y > old_y else -1

    # Проверка наличия фигур на пути
    for step in range(1, abs(new_x - old_x)):
        if board[old_x + step * step_x][old_y + step * step_y] is not None:
            return (False, board)

    # Перемещение
    board[new_x][new_y] = figure
    board[old_x][old_y] = None
    return (True, board)


def move_queen(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]

    if figure is None:
        return (False, board)
    # Логика движения ферзя - сочетание движений ладьи и слона
    if old_coords[0] == new_coords[0] or old_coords[1] == new_coords[1] and(abs(new_coords[0] - old_coords[0]) == abs(new_coords[1] - old_coords[1])):  # Движение как слон
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)
    return (False, board)

def move_king(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]

    if figure is None:
        return (False, board)

        # Логика движения короля - на одну клетку в любом направлении
    if abs(new_x - old_x) <= 1 and abs(new_y - old_y) <= 1:
        if is_valid_move(figure, old_coords, new_coords, board):  # Проверка на валидность движения
            board[new_x][new_y] = figure
            board[old_x][old_y] = None
            return (True, board)

    return (False, board)


def process_move(old_coords, new_coords, board):
    figure = board[old_coords[0]][old_coords[1]]
    if figure is None:
        return (False, board)  # Никакой фигуры на старых координатах

    # Определяем цвет фигуры
    color = 'white' if figure.isupper() else 'black'

    # Проверяем, является ли движение допустимым
    if not is_valid_move(figure, old_coords, new_coords, board):
        return (False, board)  # Ход недопустим

    # Вызов функции перемещения в зависимости от типа фигуры
    move_functions = {
        'p': move_pawn,
        'r': move_rook,
        'n': move_knight,
        'b': move_bishop,
        'q': move_queen,
        'k': move_king,
    }

    # Получаем функцию перемещения для текущей фигуры
    move_func = move_functions.get(figure.lower())
    if move_func:
        return move_func(old_coords, new_coords, board)  # Выполняем движение

    return (False, board)  # Ход не выполнен, если функция перемещения не найдена

    # Пример шахматной доски
def create_initial_board():
    board = [[None for _ in range(8)] for _ in range(8)]

        # Расстановка фигур: символы представляют фигуры
        # Цвет: 'b' - черный, 'w' - белый
    # Формат: 'тип_цвет', где тип: 'p' - пешка, 'r' - ладья, 'n' - конь, 'b' - слон, 'q' - ферзь, 'k' - король
    board[0][0] = 'r'  # Черная ладья
    board[0][1] = 'n'  # Черный конь
    board[0][2] = 'b'  # Черный слон
    board[0][3] = 'q'  # Черный ферзь
    board[0][4] = 'k'  # Черный король
    board[0][5] = 'b'  # Черный слон
    board[0][6] = 'n'  # Черный конь
    board[0][7] = 'r'  # Черная ладья

    # Черные пешки
    for i in range(8):
        board[1][i] = 'p'

        # Белые пешки
    for i in range(8):
        board[6][i] = 'P'

    board[7][0] = 'R'  # Белая ладья
    board[7][1] = 'N'  # Белый конь
    board[7][2] = 'B'  # Белый слон
    board[7][3] = 'Q'  # Белый ферзь
    board[7][4] = 'K'  # Белый король
    board[7][5] = 'B'  # Белый слон
    board[7][6] = 'N'  # Белый конь
    board[7][7] = 'R'  # Белая ладья

    return board

    # Инициализация доски
board = create_initial_board()

    # Пример движения белой пешки
# result = move_piece((1, 0), (3, 0), board)  # Пешка с позиции (6, 1) на (5, 1)
# print(result)  # Ожидается (True, board)
#
# result = move_piece((7, 0), (6, 0), board)  # Пешка с позиции (6, 1) на (5, 1)
# print(result)  # Ожидается (True, board)
#
# result = move_piece((0, 0), (2, 0), board)  # Пешка с позиции (6, 1) на (5, 1)
# print(result)  # Ожидается (True, board)

# result = move_piece((7, 3), (6, 3), board)  # Пешка с позиции (6, 1) на (5, 1)
# print(result)  # Ожидается (True, board)
#
# result = move_piece((1, 3), (2, 2), board)  # Пешка с позиции (6, 1) на (5, 1)
# print(result)  # Ожидается (True, board)
#
# result = move_piece((0, 4), (1, 3), board)  # Пешка с позиции (6, 1) на (5, 1)
# print(result)  # Ожидается (True, board)

    # Печать доски
def print_board(board):
    for row in board:
        print(" ".join(cell if cell is not None else "-" for cell in row))