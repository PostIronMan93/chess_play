from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChessGame
from .chess_logic import is_valid_move
import json

from .forms import UserRegistrationForm, UserLoginForm


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


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Замените на ваше представление с новой игрой
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
    print("ok")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('Received data:', data)

            # Проверка формата полученных данных
            if not isinstance(data, dict):
                print("Error: Received data is not a dictionary")
                return JsonResponse({'status': 'error', 'message': 'Invalid input format'}, status=400)

            # Проверка необходимых данных
            game_id = data.get('game_id')
            old_coords = data.get('old_coords', [])
            new_coords = data.get('new_coords', [])

            if not game_id or len(old_coords) != 2 or len(new_coords) != 2:
                print("Error: Missing or invalid fields")
                return JsonResponse({'status': 'error', 'message': 'Invalid input'}, status=400)

            # Получаем игру и состояние доски
            try:
                chess_game = ChessGame.objects.get(id=game_id)
            except ChessGame.DoesNotExist:
                print("Error: Game not found")

                return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)
            print(type(chess_game))
            current_turn = chess_game.turn
            board = chess_game.get_current_board()
            print(f": It's {current_turn}'s turn")
            old_x, old_y = old_coords
            new_x, new_y = new_coords
            piece = board[old_y][old_x]

            if piece is None:
                print("Error: No piece found at the given location")
                return JsonResponse({'status': 'error', 'message': 'No piece at provided coordinates'}, status=400)

            piece_color = piece.color if piece else None
            print(f"piece_color={piece_color}")
            print(f"current_turn={current_turn}")

            # Проверка на правильность очередности ходов
            if piece_color != current_turn:
                print(f"Error: It's not {current_turn}'s turn")
                return JsonResponse({'status': 'error', 'message': 'It is not your turn'}, status=403)

            # Проверка на допустимость хода
            if not is_valid_move(piece, (old_x, old_y), (new_x, new_y), board):
                print("Error: Invalid move for this piece")
                return JsonResponse({'status': 'error', 'message': 'Invalid move for this piece'}, status=400)

            # Обновляем состояние доски
            board[new_y][new_x] = piece
            board[old_y][old_x] = None

            # Сохраняем изменения
            chess_game.update_board(board)
            chess_game.turn = 'white' if current_turn == 'black' else 'black'
            chess_game.save()

            return JsonResponse({'status': 'success', 'message': 'Move made successfully'})

        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    print("Error: Invalid request method")
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



def new_game(request):
    # Инициализируем начальное состояние доски
    initial_board = [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"]
    ]
    # Создаем новую игру в БД
    game = ChessGame.objects.create(board_state=json.dumps(initial_board), turn='white')

    # Возвращаем клиенту ID новой игры (чтобы потом отправлять его в запросах)
    return redirect('index', game_id=game.id)


# def continue_game(request):
#     # Логика по извлечению текущей игры и отображению
#     return render(request, 'chess/continue_game.html')  # Создайте этот шаблон
