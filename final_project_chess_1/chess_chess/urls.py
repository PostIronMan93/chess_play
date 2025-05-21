from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('move_piece/', views.move_piece, name='move_piece'),
    path('new_game/', views.new_game, name='new_game'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('index/<int:game_id>/', views.index, name='index'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    # path('continue_game/', views.continue_game, name='continue_game'),
]

