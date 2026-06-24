from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Entrega, Rota, Veiculo, Motorista, Cliente
from datetime import date

class RegraCapacidadeTest(TestCase):
    def setUp(self):
        self.motorista = Motorista.objects.create(nome="Motorista Teste", cpf="12345678900")
        self.veiculo = Veiculo.objects.create(
            placa="TEST-0001", modelo="Caminhão P", tipo="CAMINHAO", 
            capacidade_maxima=100.00, km_atual=1000
        )
        self.rota = Rota.objects.create(
            nome="Rota Teste", motorista=self.motorista, veiculo=self.veiculo, data_rota=date.today()
        )
        self.cliente = Cliente.objects.create(nome="Cliente Teste", endereco="Rua A")

    def test_bloqueio_sobrecarga(self):
        # Cria entrega de 80kg (OK)
        e1 = Entrega(codigo_rastreio="CX-01", cliente=self.cliente, rota=self.rota, endereco_destino="Rua B", capacidade_necessaria=80.00, valor_frete=50.00, data_entrega_prevista=date.today())
        e1.full_clean()
        e1.save()
        
        # Tenta criar +30kg (Total 110kg > 100kg -> ERRO)
        e2 = Entrega(codigo_rastreio="CX-02", cliente=self.cliente, rota=self.rota, endereco_destino="Rua C", capacidade_necessaria=30.00, valor_frete=50.00, data_entrega_prevista=date.today())
        
        with self.assertRaises(ValidationError):
            e2.full_clean()
            e2.save()