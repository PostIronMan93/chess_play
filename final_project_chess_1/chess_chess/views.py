from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from .models import ChessGame, Piece
from .chess_logic import is_valid_move
import json, logging

from .forms import UserRegistrationForm, UserLoginForm

logger = logging.getLogger(__name__)
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'chess/register.html', {'form': form})

def is_valid_coordinates(coords):
    return (
        isinstance(coords, list) and
        len(coords) == 2 and
        all(isinstance(coord, int) for coord in coords) and
        all(0 <= coord < 8 for coord in coords)
    )
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  
            else:
                return render(request, 'chess/login.html', {'form': form, 'error': 'Неверные логин или пароль'})
    else:
        form = UserLoginForm()
    return render(request, 'chess/login.html', {'form': form})

def home(request):
    return render(request, 'chess/home.html')

def dashboard(request):
    return render(request, 'chess/dashboard.html')


def index(request, game_id):
    return render(request, 'chess/index.html', {'game_id': game_id})


@csrf_exempt
def move_piece(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
        logger.debug(f"Received move request: {data}")

        game_id = data.get('game_id')
        old_coords = data.get('old_coords')
        new_coords = data.get('new_coords')
        castle = data.get('castle', False)
        promotion = data.get('promotion')

        if not game_id or not old_coords or not new_coords:
            return JsonResponse({'status': 'error', 'message': 'Missing required parameters'}, status=400)

        if len(old_coords) != 2 or len(new_coords) != 2:
            return JsonResponse({'status': 'error', 'message': 'Invalid coordinates format'}, status=400)

        old_x, old_y = old_coords
        new_x, new_y = new_coords

        # Проверяем координаты в пределах доски
        if not all(isinstance(c, int) and 0 <= c < 8 for c in [old_x, old_y, new_x, new_y]):
            return JsonResponse({'status': 'error', 'message': 'Coordinates out of bounds'}, status=400)

        # Получаем игру
        try:
            chess_game = ChessGame.objects.get(id=game_id)
        except ChessGame.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)

        current_turn = chess_game.turn
        board = chess_game.get_current_board()  # предполагается, что возвращает 2D-массив с фигурами

        piece = board[old_y][old_x]
        if piece is None:
            return JsonResponse({'status': 'error', 'message': 'No piece at old_coords'}, status=400)

        if piece.color != current_turn:
            return JsonResponse({'status': 'error', 'message': 'It is not your turn'}, status=403)

        # Обработка рокировки
        if castle:
            if piece.type.lower() != 'k':
                return JsonResponse({'status': 'error', 'message': 'Castling move must be done by king'}, status=400)

            dx = new_x - old_x
            dy = new_y - old_y
            # Рокировка — король ходит на 2 клетки по горизонтали, y не меняется
            if dy != 0 or abs(dx) != 2:
                return JsonResponse({'status': 'error', 'message': 'Invalid castling move coordinates'}, status=400)

            rook_old_x = 7 if dx > 0 else 0
            rook_new_x = old_x + (1 if dx > 0 else -1)
            rook = board[old_y][rook_old_x]

            if rook is None or rook.type.lower() != 'r':
                return JsonResponse({'status': 'error', 'message': 'No rook to castle with'}, status=400)

            if getattr(piece, 'has_moved', True) or getattr(rook, 'has_moved', True):
                return JsonResponse({'status': 'error', 'message': 'King or rook has already moved'}, status=400)

            # Совершаем рокировку
            board[new_y][new_x] = piece
            board[old_y][old_x] = None
            piece.has_moved = True

            board[old_y][rook_new_x] = rook
            board[old_y][rook_old_x] = None
            rook.has_moved = True

            # Сохраняем состояние доски
            chess_game.update_board(board)
            chess_game.turn = 'black' if current_turn == 'white' else 'white'
            chess_game.save()

            logger.debug("Castling move performed successfully")
            return JsonResponse({
                'status': 'success',
                'message': 'Castling move done',
                'boardState': json.loads(chess_game.board_state),
                'next_turn': chess_game.turn
            })

        # Обычный ход
        # Проверяем валидность хода (предполагается, что есть функция is_valid_move)
        if not is_valid_move(piece, (old_x, old_y), (new_x, new_y), board):
            return JsonResponse({'status': 'error', 'message': 'Invalid move for this piece'}, status=400)

        if piece.type.lower() == 'p':
            last_rank = 0 if piece.color == 'white' else 7
            if new_y == last_rank:
                if promotion not in ['queen', 'rook', 'bishop', 'knight']:
                    # Если promotion не указан или некорректен, по умолчанию ферзь
                    promotion = 'queen'
                # Заменяем пешку на выбранную фигуру
                piece.type = promotion[0]

                
        board[new_y][new_x] = piece
        board[old_y][old_x] = None

        if not getattr(piece, 'has_moved', False):
            piece.has_moved = True

        chess_game.update_board(board)
        chess_game.turn = 'black' if current_turn == 'white' else 'white'
        chess_game.save()

        logger.debug("Regular move performed successfully")
        return JsonResponse({
            'status': 'success',
            'message': 'Move made successfully',
            'boardState': json.loads(chess_game.board_state),
            'next_turn': chess_game.turn
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Exception in move_piece: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
def initial_board_state():
    pieces_row_black = [
        {"type": "r", "color": "black", "hasMoved": False},
        {"type": "n", "color": "black", "hasMoved": False},
        {"type": "b", "color": "black", "hasMoved": False},
        {"type": "q", "color": "black", "hasMoved": False},
        {"type": "k", "color": "black", "hasMoved": False},
        {"type": "b", "color": "black", "hasMoved": False},
        {"type": "n", "color": "black", "hasMoved": False},
        {"type": "r", "color": "black", "hasMoved": False},
    ]
    pawns_black = [{"type": "p", "color": "black", "hasMoved": False} for _ in range(8)]
    empty_row = [None for _ in range(8)]
    pawns_white = [{"type": "p", "color": "white", "hasMoved": False} for _ in range(8)]
    pieces_row_white = [
        {"type": "r", "color": "white", "hasMoved": False},
        {"type": "n", "color": "white", "hasMoved": False},
        {"type": "b", "color": "white", "hasMoved": False},
        {"type": "q", "color": "white", "hasMoved": False},
        {"type": "k", "color": "white", "hasMoved": False},
        {"type": "b", "color": "white", "hasMoved": False},
        {"type": "n", "color": "white", "hasMoved": False},
        {"type": "r", "color": "white", "hasMoved": False},
    ]

    board = [
        pieces_row_black,
        pawns_black,
        empty_row.copy(),
        empty_row.copy(),
        empty_row.copy(),
        empty_row.copy(),
        pawns_white,
        pieces_row_white
    ]
    return board

def new_game(request):
    board = initial_board_state()
    game = ChessGame.objects.create(board_state=json.dumps(board), turn='white')
    return redirect('index', game_id=game.id)
