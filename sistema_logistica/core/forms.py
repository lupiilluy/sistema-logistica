from django import forms
from .models import Entrega

class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        # Definimos APENAS os campos que o motorista pode mexer
        fields = ['status', 'data_entrega_real', 'observacoes']
        
        # Widgets ajudam a deixar o calendário bonitinho (tipo date)
        widgets = {
            'data_entrega_real': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }