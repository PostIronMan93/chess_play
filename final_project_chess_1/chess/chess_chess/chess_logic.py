#проверка на валидность хода
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
    if target is not None and target.color == figure.color:  # проверяем цвет
        print("Cannot move to a square occupied by own piece")
        return False
    return True

def move_pawn(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]

    if figure is None:
        return (False, board)
    # направление движения пешки
    direction = 1 if figure.islower() else -1

    # движение на 1 клетку вперёд
    if new_x == old_x + direction and new_y == old_y and board[new_x][new_y] is None:
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)

    # движение на 2 клетки вперёд (если до этого не ходил пешкой)
    if (old_x == 6 and figure.isupper() and new_x == 4 and new_y == old_y and board[5][old_y] is None and board[4][old_y] is None) or \
       (old_x == 1 and figure.islower() and new_x == 3 and new_y == old_y and board[2][old_y] is None and board[3][old_y] is None):
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)

    # взятие пешкой (берут по диагонали)
    if new_x == old_x + direction and abs(new_y - old_y) == 1 and board[new_x][new_y] is not None:
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)

    return (False, board)

def move_rook(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]
    direction_x = new_x - old_x
    direction_y = new_y - old_y

    # движение ладьи (только вперёд-назад/влево-вправо)
    if not (direction_x == 0 or direction_y == 0):
        return (False, board)

    # Проверка, есть ли фигуры на пути
    step_x = (direction_x // abs(direction_x)) if direction_x != 0 else 0
    step_y = (direction_y // abs(direction_y)) if direction_y != 0 else 0

    for i in range(1, max(abs(direction_x), abs(direction_y))):
        if board[old_x + i * step_x][old_y + i * step_y] is not None:
            return (False, board)

    board[new_x][new_y] = figure
    board[old_x][old_y] = None
    return (True, board)

def move_knight(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]

    # ходит буквой "Г" - две клетки в одном направлении и одну в другом
    if (abs(new_x - old_x) == 2 and abs(new_y - old_y) == 1) or (abs(new_x - old_x) == 1 and abs(new_y - old_y) == 2):
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)

    return (False, board)

def move_bishop(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]
    direction_x = new_x - old_x
    direction_y = new_y - old_y

    # движение только по диагонали
    if abs(direction_x) != abs(direction_y):
        return (False, board)

        # Проверка, есть ли фигуры на пути
    step_x = direction_x // abs(direction_x)
    step_y = direction_y // abs(direction_y)

    for i in range(1, abs(direction_x)):
        if board[old_x + i * step_x][old_y + i * step_y] is not None:
            return (False, board)

    board[new_x][new_y] = figure
    board[old_x][old_y] = None
    return (True, board)


def move_queen(old_coords, new_coords, board):
    # движение ферзя -> логика слона + ладьи
    if move_rook(old_coords, new_coords, board)[0] or move_bishop(old_coords, new_coords, board)[0]:
        return (True, board)
    return (False, board)


def move_king(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_x][old_y]

    # движение короля - на одну клетку в любом направлении
    if abs(new_x - old_x) <= 1 and abs(new_y - old_y) <= 1:
        board[new_x][new_y] = figure
        board[old_x][old_y] = None
        return (True, board)

    return (False, board)

# функция, которая отвечает за возможность движение фигуры (после проверки валидности, в случае если ход валидный)
def process_move(old_coords, new_coords, board, current_turn):
    figure = board[old_coords[0]][old_coords[1]]
    if figure is None:
        return (False, board)  # Никакой фигуры на старых координатах

    # цвет фигуры
    figure_color = 'white' if figure.isupper() else 'black'
    if (current_turn == 'white' and figure_color != 'white') or \
            (current_turn == 'black' and figure_color != 'black'):
        print(f"It's {current_turn}'s turn, cannot move {figure_color} piece")
        return False, board  # Неверный ход

    # является ли движение допустимым
    if not is_valid_move(figure, old_coords, new_coords, board):
        return (False, board)  # Ход недопустим

    # вызов функции перемещения в зависимости от типа фигуры
    move_functions = {
        'p': move_pawn,
        'r': move_rook,
        'n': move_knight,
        'b': move_bishop,
        'q': move_queen,
        'k': move_king,
    }

    # получание функции перемещения для текущей фигуры
    move_func = move_functions.get(figure.lower())
    if move_func:
        result, updated_board = move_func(old_coords, new_coords, board)
        if result:
            return (True, updated_board)

    return (False, board)  # ход не выполнен, если функция перемещения не найдена


def create_initial_board():
    board = [[None for _ in range(8)] for _ in range(8)]
    # Расстановка фигур
    board[0][0] = 'r'  # Черная ладья
    board[0][1] = 'n'  # Черный конь
    board[0][2] = 'b'  # Черный слон
    board[0][3] = 'q'  # Черная ферзь
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
    board[7][3] = 'Q'  # Белая ферзь
    board[7][4] = 'K'  # Белый король
    board[7][5] = 'B'  # Белый слон
    board[7][6] = 'N'  # Белый конь
    board[7][7] = 'R'  # Белая ладья

    return board

    # Инициализация доски


board = create_initial_board()
current_turn = 'white'  # Начинаем с белых


# Печать доски
def print_board(board):
    for row in board:
        print(" ".join(cell if cell is not None else "-" for cell in row))


print_board(board)


