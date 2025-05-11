from django.db import models
import json

class ChessGame(models.Model):
    board_state = models.TextField()  # Состояние доски в виде JSON
    turn = models.CharField(max_length=5)  # 'white' или 'black'

    def get_current_board(self):
        """Получаем текущее состояние доски в формате 2D списка."""
        return json.loads(self.board_state)

    def update_board(self, new_board):
        """Обновляем состояние доски и добавляем ход в историю."""
        self.board_state = json.dumps(new_board)  # Преобразуем 2D список в JSON
        # Добавляем новый ход в историю
        # history = json.loads(self.move_history)
        # history.append(move)
        # self.move_history = json.dumps(history)  # Сохраняем обновленную историю
        self.save()