from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('move_piece/', views.move_piece, name='move_piece'),
    path('new_game/', views.new_game, name='new_game'),
]

