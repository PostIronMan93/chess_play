from django.urls import path
from .views import index, move_piece

urlpatterns = [
    path('', index, name='index'),
    path('move_piece/', move_piece, name='move_piece'),
]

