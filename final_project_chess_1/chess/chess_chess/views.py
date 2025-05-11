from django.shortcuts import render
from django.http import JsonResponse
from .models import ChessGame
from .chess_logic import process_move, is_valid_move  # Подразумеваем, что функция move_piece корректно реализована
import json
from django.views.decorators.csrf import csrf_exempt

def index(request):
    game_id = 746
    return render(request, 'chess/index.html', {'game_id': game_id})

@csrf_exempt
def move_piece(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            game_id = data.get('game_id')
            if not game_id:
                return JsonResponse({'status': 'error', 'message': 'No game_id provided'}, status=400)

            old_coords = data.get('old_coords', {})
            new_coords = data.get('new_coords', {})

            old_x = old_coords.get('x')
            old_y = old_coords.get('y')
            new_x = new_coords.get('x')
            new_y = new_coords.get('y')

            if not all(isinstance(coord, int) for coord in [old_x, old_y, new_x, new_y]):
                return JsonResponse({'status': 'error', 'message': 'Invalid coordinates'}, status=400)

            chess_game = ChessGame.objects.get(id=game_id)
            board = chess_game.get_current_board()

            print(f"Current board: {board}")  # Отладочный вывод
            print(f"Checking figure at old coords: {old_y},{old_x}")

            if (old_x, old_y) == (new_x, new_y):
                return JsonResponse({'status': 'invalid move', 'message': 'Cannot move to the same position'}, status=400)

            figure = board[old_y][old_x]
            if not figure:
                return JsonResponse({'status': 'error', 'message': 'No figure at old coordinates'}, status=400)

            current_turn = chess_game.turn
            if current_turn != figure.color:
                return JsonResponse({'status': 'error', 'message': f"It's {current_turn}'s turn"}, status=400)

            target_figure = board[new_y][new_x]
            if target_figure and target_figure.color == figure.color:
                return JsonResponse({'status': 'error', 'message': 'Cannot move to a square occupied by own piece'}, status=400)

            if not is_valid_move(figure, (old_x, old_y), (new_x, new_y), board):
                return JsonResponse({'status': 'invalid move'}, status=400)

            success, new_board = process_move(old_coords, new_coords, board)
            if not success:
                return JsonResponse({'status': 'invalid move'}, status=400)

            chess_game.update_board(new_board)
            chess_game.turn = 'black' if chess_game.turn == 'white' else 'white'
            chess_game.save()

            return JsonResponse({'status': 'success', 'board': new_board})

        except ChessGame.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

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
    return JsonResponse({'status': 'success', 'game_id': game.id})