from django.shortcuts import render
from django.http import JsonResponse
from .models import ChessGame
from .chess_logic import is_valid_move
import json
from django.views.decorators.csrf import csrf_exempt

def index(request):
    game_id = 746
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
            piece = board[old_x][old_y]
            print(f"Error: It's not {current_turn}'s turn")

            if piece is None:
                print("Error: No piece found at the given location")
                return JsonResponse({'status': 'error', 'message': 'No piece at provided coordinates'}, status=400)

            piece_color = piece.color if piece else None

            # Проверка на правильность очередности ходов
            if piece_color != current_turn:
                print(f"Error: It's not {current_turn}'s turn")
                return JsonResponse({'status': 'error', 'message': 'It is not your turn'}, status=403)

            # Проверка на допустимость хода
            if not is_valid_move(piece, (old_x, old_y), (new_x, new_y), board):
                print("Error: Invalid move for this piece")
                return JsonResponse({'status': 'error', 'message': 'Invalid move for this piece'}, status=400)

            # Обновляем состояние доски
            board[new_x][new_y] = piece
            board[old_x][old_y] = None

            # Сохраняем изменения
            chess_game.update_board(board)
            chess_game.turn = 'black' if current_turn == 'white' else 'white'
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
    return JsonResponse({'status': 'success', 'game_id': game.id})
