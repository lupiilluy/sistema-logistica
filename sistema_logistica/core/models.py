from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# 1. ENTIDADES AUXILIARES (Para Status e Tipos)
class StatusEntrega(models.TextChoices):
    PENDENTE = 'PENDENTE', 'Pendente'
    EM_TRANSITO = 'EM_TRANSITO', 'Em Trânsito'
    ENTREGUE = 'ENTREGUE', 'Entregue'
    CANCELADA = 'CANCELADA', 'Cancelada'
    REMARCADA = 'REMARCADA', 'Remarcada'

class StatusMotorista(models.TextChoices):
    ATIVO = 'ATIVO', 'Ativo'
    INATIVO = 'INATIVO', 'Inativo'
    EM_ROTA = 'EM_ROTA', 'Em Rota'
    DISPONIVEL = 'DISPONIVEL', 'Disponível'

class TipoVeiculo(models.TextChoices):
    CARRO = 'CARRO', 'Carro'
    VAN = 'VAN', 'Van'
    CAMINHAO = 'CAMINHAO', 'Caminhão'

# 2. MODELOS PRINCIPAIS

class Cliente(models.Model):
    # Simplificação: Vincula a um usuário de login do Django
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    
    def __str__(self):
        return self.nome

class Motorista(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='motorista')
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    cnh = models.CharField(max_length=20, choices=[('B','B'), ('C','C'), ('D','D'), ('E','E')])
    telefone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=StatusMotorista.choices, default=StatusMotorista.DISPONIVEL)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.status})"

class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TipoVeiculo.choices)
    capacidade_maxima = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unidades de carga")
    km_atual = models.DecimalField(max_digits=10, decimal_places=1)
    # Status "manutenção" pode ser adicionado se necessário, usando boolean ou choices
    em_manutencao = models.BooleanField(default=False)
    
    # Relacionamento 1:1 conforme documento [cite: 121] e [cite: 70]
    motorista_ativo = models.OneToOneField(
        Motorista, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='veiculo_atual'
    )

    def __str__(self):
        return f"{self.modelo} - {self.placa}"

class Rota(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    
    # Relacionamentos exigidos [cite: 108, 111]
    motorista = models.ForeignKey(Motorista, on_delete=models.PROTECT, related_name='rotas')
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, related_name='rotas')
    
    data_rota = models.DateField()
    status = models.CharField(max_length=20, default='PLANEJADA') # Planejada, Em andamento, Concluída
    
    # Campos calculados (podem ser atualizados via signals ou métodos)
    km_total_estimado = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    tempo_estimado = models.DurationField(null=True, blank=True)

    def capacidade_total_utilizada(self):
        # Soma a capacidade necessária de todas as entregas desta rota
        return sum(entrega.capacidade_necessaria for entrega in self.entregas.all())

    def clean(self):
        # Validação cruzada básica (Motorista deve ser o mesmo do veículo?)
        if self.veiculo.motorista_ativo and self.veiculo.motorista_ativo != self.motorista:
            raise ValidationError("O veículo selecionado está vinculado a outro motorista ativo.")

    def __str__(self):
        return f"Rota: {self.nome} - {self.motorista}"

class Entrega(models.Model):
    codigo_rastreio = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='entregas') # [cite: 60]
    
    # Rota é opcional no início (null=True), pois a entrega nasce "sem rota" [cite: 116]
    rota = models.ForeignKey(Rota, on_delete=models.SET_NULL, null=True, blank=True, related_name='entregas')
    
    endereco_origem = models.CharField(max_length=200, default="Galpão Principal")
    endereco_destino = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=StatusEntrega.choices, default=StatusEntrega.PENDENTE)
    
    capacidade_necessaria = models.DecimalField(max_digits=10, decimal_places=2) # [cite: 88]
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2)
    
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_entrega_prevista = models.DateField()
    data_entrega_real = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)

    def clean(self):
        # Validação de Capacidade [cite: 117]
        # "Soma(capacidade_necessaria) <= capacidade_maxima do veículo"
        if self.rota and self.rota.veiculo:
            capacidade_veiculo = self.rota.veiculo.capacidade_maxima
            # Pega todas as entregas da rota JÁ salvas + esta atual
            entregas_rota = self.rota.entregas.exclude(id=self.id)
            total_atual = sum(e.capacidade_necessaria for e in entregas_rota)
            
            if total_atual + self.capacidade_necessaria > capacidade_veiculo:
                raise ValidationError(f"Capacidade do veículo excedida! Máx: {capacidade_veiculo}, Atual: {total_atual + self.capacidade_necessaria}")

    def __str__(self):
        return f"#{self.codigo_rastreio} - {self.status}"