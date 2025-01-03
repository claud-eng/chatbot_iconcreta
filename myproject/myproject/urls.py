"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from chatbot.views import chatbot_index # Importa la vista principal del chatbot
from django.contrib import admin # Importa la interfaz de administración de Django
from django.urls import path, include # Permite definir y enlazar rutas de URL

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chatbot/', include('chatbot.urls')),  # Incluye las URL de tu aplicación chatbot
    path('', chatbot_index, name='home'),  # Asigna la vista chat_view a la URL raíz
]