from django.urls import path # Importa la función para definir rutas de URL
from django.views.generic import TemplateView # Importa una vista genérica basada en plantillas
from .views import flujo_dptos_casas, chatbot_index # Importa las vistas flujo de departamentos y chatbot principal

urlpatterns = [
    # otras urls...
    path('flujo_dptos_casas/', flujo_dptos_casas, name='flujo_dptos_casas'),
    path('chatbot_index/', chatbot_index, name='chatbot_index'),  
    path('test-chatbot/', TemplateView.as_view(template_name="test_chatbot.html")),
]