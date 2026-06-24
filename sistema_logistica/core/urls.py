from django.urls import path
from . import views

urlpatterns = [
    # A raiz (http://127.0.0.1:8000/) agora abre a tela azul (Index)
    path('', views.index, name='index'),

    # O endereço /funcionario/ abre a lista de entregas (antiga Home)
    path('funcionario/', views.lista_entregas, name='home'),

    # As outras rotas continuam iguais
    path('entrega/editar/<int:id>/', views.editar_entrega, name='editar_entrega'),
    path('rastreamento/', views.rastreamento, name='rastreamento'),
]