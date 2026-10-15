from django.http import JsonResponse
from django.urls import include, path, re_path


def not_found(request):
    return JsonResponse({'detail': 'Rota não encontrada.'}, status=404)


urlpatterns = [
    path('', include('library.urls')),
    re_path(r'^.*$', not_found),  # precisa ser a ÚLTIMA rota
]
