from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Entrega
from .forms import EntregaForm

# Tela Inicial (Dashboard do Funcionário)
@login_required
def lista_entregas(request):
    # Se for Superusuário (Dono), vê tudo
    if request.user.is_superuser:
        entregas = Entrega.objects.all()
    # Se for Motorista (tem vínculo na tabela Motorista), vê só as dele
    elif hasattr(request.user, 'motorista'):
        entregas = Entrega.objects.filter(rota__motorista=request.user.motorista)
    # Se não tiver perfil, não vê nada
    else:
        entregas = Entrega.objects.none()
        
    return render(request, 'core/lista_entregas.html', {'entregas': entregas})

# Tela de Edição de Entrega
@login_required
def editar_entrega(request, id):
    entrega = get_object_or_404(Entrega, id=id)

    # Validação de Segurança
    if not request.user.is_superuser:
        if not hasattr(request.user, 'motorista') or entrega.rota.motorista != request.user.motorista:
            return HttpResponseForbidden("Você não tem permissão para editar esta entrega.")

    if request.method == 'POST':
        form = EntregaForm(request.POST, instance=entrega)
        if form.is_valid():
            form.save()
            # --- LINHA NOVA ABAIXO ---
            messages.success(request, "✅ Status da entrega atualizado com sucesso!")
            # -------------------------
            return redirect('home')
    else:
        form = EntregaForm(instance=entrega)

    return render(request, 'core/form_entrega.html', {'form': form, 'entrega': entrega})

# Tela Pública de Rastreamento
def rastreamento(request):
    codigo = request.GET.get('codigo')
    entrega = None
    if codigo:
        entrega = Entrega.objects.filter(codigo_rastreio=codigo).first()
    return render(request, 'core/rastreamento.html', {'entrega': entrega, 'codigo': codigo})

# Tela Home (Botões Iniciais)
def index(request):
    return render(request, 'core/index.html')