from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # <--- Adicione esta linha
    path('', include('core.urls')),
]

def index(request):
    return render(request, 'core/index.html')