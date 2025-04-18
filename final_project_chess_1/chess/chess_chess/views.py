from django.shortcuts import render
from django.http import JsonResponse
from .models import ChessGame
from .chess_logic import ChessBoard, Pawn, King


def index(request):
    return render(request, 'chess/index.html')


def move_piece(request):
    if request.method == 'POST':
        data = request.POST
        chess_game = ChessGame.objects.get(id=data['game_id'])  # Получаем игру
        board = ChessBoard()

        start_position = (int(data['start_x']), int(data['start_y']))
        new_position = (int(data['new_x']), int(data['new_y']))

        current_piece = board.board[start_position[0]][start_position[1]]

        chess_game.turn = 'white' if chess_game.turn == 'black' else 'black'
        chess_game.save()

        if current_piece and (new_position in current_piece.valid_moves(start_position, board)):
            # Проверяем рокировку
            if isinstance(current_piece, King) and abs(new_position[1] - start_position[1]) == 2:
                if board.perform_castle(start_position, (start_position[0], new_position[1])):
                    return JsonResponse({'status': 'success'})
            else:
                # Перемещение фигуры
                board.board[new_position[0]][new_position[1]] = current_piece
                board.board[start_position[0]][start_position[1]] = None

                # Проверка на превращение пешки
                if isinstance(current_piece, Pawn):
                    if (current_piece.color == 'white' and new_position[1] == 0) or (current_piece.color == 'black' and new_position[1] == 7):
                        new_piece = current_piece.promote()
                        board.board[new_position[0]][new_position[1]] = new_piece

                # Проверка на шах и мат
                if board.is_in_check('black'):
                    return JsonResponse({'status': 'check', 'color': 'black'})
                elif board.is_checkmate('black'):
                    return JsonResponse({'status': 'checkmate', 'color': 'black'})

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'invalid move'}, status=400)

    return JsonResponse({'status': 'error'}, status=400)

