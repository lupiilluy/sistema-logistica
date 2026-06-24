from django.contrib import admin
from .models import Entrega, Motorista, Rota, Veiculo, Cliente

# Configurando o visual do Cliente
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'usuario')

# Configurando o visual do Motorista
@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'cnh', 'status')
    list_filter = ('status',)

# Configurando o visual do Veículo
@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'placa', 'tipo', 'capacidade_maxima')

# Configurando o visual da Rota
@admin.register(Rota)
class RotaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'motorista', 'veiculo', 'data_rota')

# Configurando o visual da Entrega
@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('codigo_rastreio', 'cliente', 'rota', 'status')