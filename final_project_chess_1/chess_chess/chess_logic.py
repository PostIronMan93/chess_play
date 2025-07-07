#проверка на валидность хода
moved_figures = set()
last_double_pawn_move = None
moved_figures = {
    'white_king': False,
    'white_rook_left': False,
    'white_rook_right': False,
    'black_king': False,
    'black_rook_left': False,
    'black_rook_right': False,
}
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
    target = board[new_coords[1]][new_coords[0]]
    if target is not None and target.color == figure.color:  # проверяем цвет
        print("Cannot move to a square occupied by own piece")
        return False
    return True

def move_pawn(old_coords, new_coords, board):
    global last_double_pawn_move

    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_y][old_x]

    if figure is None:
        return (False, board)

    direction = 1 if figure.islower() else -1  # направление движения пешки

    # движение на 1 клетку вперёд
    if new_x == old_x and new_y == old_y + direction and board[new_y][new_x] is None:
        board[new_y][new_x] = figure
        board[old_y][old_x] = None
        last_double_pawn_move = None
        return (True, board)

    # движение на 2 клетки вперёд (если пешка на стартовой позиции)
    if (old_y == 1 and figure.islower() and new_y == old_y + 2 and new_x == old_x and
            board[old_y + 1][old_x] is None and board[new_y][new_x] is None):
        board[new_y][new_x] = figure
        board[old_y][old_x] = None
        last_double_pawn_move = (new_x, new_y)
        return (True, board)

    if (old_y == 6 and figure.isupper() and new_y == old_y - 2 and new_x == old_x and
            board[old_y - 1][old_x] is None and board[new_y][new_x] is None):
        board[new_y][new_x] = figure
        board[old_y][old_x] = None
        last_double_pawn_move = (new_x, new_y)
        return (True, board)

    # взятие пешкой по диагонали (обычное)
    if abs(new_x - old_x) == 1 and new_y == old_y + direction:
        target = board[new_y][new_x]
        if target is not None and target.isupper() != figure.isupper():
            board[new_y][new_x] = figure
            board[old_y][old_x] = None
            last_double_pawn_move = None
            return (True, board)

        # взятие на проходе
        if last_double_pawn_move == (new_x, old_y):
            # снимаем пешку, которая сделала двойной ход
            board[old_y][new_x] = None
            board[new_y][new_x] = figure
            board[old_y][old_x] = None
            last_double_pawn_move = None
            return (True, board)

    return (False, board)

def move_rook(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_y][old_x]
    direction_x = new_x - old_x
    direction_y = new_y - old_y

    # движение ладьи (только вперёд-назад/влево-вправо)
    if not (direction_x == 0 or direction_y == 0):
        return (False, board)

    # Проверка, есть ли фигуры на пути
    step_x = (direction_x // abs(direction_x)) if direction_x != 0 else 0
    step_y = (direction_y // abs(direction_y)) if direction_y != 0 else 0

    for i in range(1, max(abs(direction_x), abs(direction_y))):
        if board[old_y + i * step_y][old_x + i * step_x] is not None:
            return (False, board)

    board[new_y][new_x] = figure
    board[old_y][old_x] = None

    color = 'white' if figure.isupper() else 'black'
    if old_x == 0:  # левая ладья
        moved_figures[f'{color}_rook_left'] = True
    elif old_x == 7:  # правая ладья
        moved_figures[f'{color}_rook_right'] = True

    return (True, board)

def move_knight(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_y][old_x]

    # ходит буквой "Г" - две клетки в одном направлении и одну влево-вправо после продвижения на 2 клетки
    if (abs(new_x - old_x) == 2 and abs(new_y - old_y) == 1) or \
            (abs(new_x - old_x) == 1 and abs(new_y - old_y) == 2):
        target = board[new_y][new_x]
        if target is None or target.color != figure.color:
            board[new_y][new_x] = figure
            board[old_y][old_x] = None
            return (True, board)

    return (False, board)

def move_bishop(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_y][old_x]

    direction_x = new_x - old_x
    direction_y = new_y - old_y

    # движение только по диагонали
    if abs(direction_x) != abs(direction_y):
        return (False, board)

        # Проверка, есть ли фигуры на пути
    step_x = direction_x // abs(direction_x)
    step_y = direction_y // abs(direction_y)

    for i in range(1, abs(direction_x)):
        if board[old_y + i * step_y][old_x + i * step_x] is not None:
            return (False, board)

    target = board[new_y][new_x]
    # Можно перемещаться на занятую клетку, если это фигура противника
    if target is None or target.color != figure.color:
        board[new_y][new_x] = figure
        board[old_y][old_x] = None
        return (True, board)
    return (False, board)

def move_queen(old_coords, new_coords, board):
    # движение ферзя -> логика слона + ладьи
    if move_rook(old_coords, new_coords, board)[0] or move_bishop(old_coords, new_coords, board)[0]:
        return (True, board)
    return (False, board)


def move_king(old_coords, new_coords, board):
    old_x, old_y = old_coords
    new_x, new_y = new_coords
    figure = board[old_y][old_x]

    dx = new_x - old_x
    dy = new_y - old_y

    color = 'white' if figure.isupper() else 'black'

    # Рокировка - король двигается на 2 клетки по горизонтали
    if dy == 0 and abs(dx) == 2:
        # Проверяем, что король и ладья не ходили
        if moved_figures[f'{color}_king']:
            print("Король уже ходил - рокировка невозможна")
            return (False, board)

        # Определяем сторону рокировки
        if dx == 2:
            rook_x = 7
            rook_key = f'{color}_rook_right'
            new_rook_x = new_x - 1
        else:
            rook_x = 0
            rook_key = f'{color}_rook_left'
            new_rook_x = new_x + 1

        rook = board[old_y][rook_x]
        if rook is None or (rook.upper() != 'R'):
            print("Ладья отсутствует для рокировки")
            return (False, board)
        if moved_figures[rook_key]:
            print("Ладья уже ходила - рокировка невозможна")
            return (False, board)

        # Проверяем пустоту клеток между королём и ладьёй
        step = 1 if dx > 0 else -1
        for x in range(old_x + step, rook_x, step):
            if board[old_y][x] is not None:
                print("Путь между королём и ладьёй не пуст")
                return (False, board)


        # Выполняем рокировку
        board[old_y][new_x] = figure
        board[old_y][old_x] = None
        board[old_y][new_rook_x] = rook
        board[old_y][rook_x] = None

        # Отмечаем, что король и ладья ходили
        moved_figures[f'{color}_king'] = True
        moved_figures[rook_key] = True

        print(f"Рокировка {color} выполнена")
        return (True, board)

    # Обычное движение короля - на 1 клетку в любом направлении
    if abs(dx) <= 1 and abs(dy) <= 1:
        target = board[new_y][new_x]
        if target is None or target.isupper() != figure.isupper():
            board[new_y][new_x] = figure
            board[old_y][old_x] = None
            moved_figures[f'{color}_king'] = True
            return (True, board)

    return (False, board)

# функция, которая отвечает за возможность движение фигуры (после проверки валидности, в случае если ход валидный)
def process_move(old_coords, new_coords, board, current_turn):
    global last_double_pawn_move

    figure = board[old_coords[1]][old_coords[0]]
    if figure is None:
        return (False, board)

    figure_color = 'white' if figure.isupper() else 'black'
    if (current_turn == 'white' and figure_color != 'white') or \
       (current_turn == 'black' and figure_color != 'black'):
        return (False, board)

    if not is_valid_move(figure, old_coords, new_coords, board):
        return (False, board)

    move_functions = {
        'p': move_pawn,
        'r': move_rook,
        'n': move_knight,
        'b': move_bishop,
        'q': move_queen,
        'k': move_king,
    }

    move_func = move_functions.get(figure.lower())
    if move_func:
        result, updated_board = move_func(old_coords, new_coords, board)
        if result:
            # Если ход пешкой и был двойной ход — last_double_pawn_move уже установлен иначе сбрасываем
            if figure.lower() != 'p' or abs(new_coords[1] - old_coords[1]) != 2:
                last_double_pawn_move = None
            return (True, updated_board)

    return (False, board)


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

