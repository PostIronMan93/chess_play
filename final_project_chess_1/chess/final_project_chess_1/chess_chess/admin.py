from django.contrib import admin

from .models import ChessGame

class ChessGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'turn', 'board_state', 'move_history')

admin.site.register(ChessGame, ChessGameAdmin)
