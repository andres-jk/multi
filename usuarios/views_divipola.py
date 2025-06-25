from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models_divipola import Departamento, Municipio

@require_http_methods(["GET"])
def get_municipios(request):
    """Vista para obtener los municipios de un departamento específico"""
    departamento_id = request.GET.get('departamento_id')
    if not departamento_id:
        return JsonResponse({'error': 'Departamento no especificado'}, status=400)
    
    try:
        municipios = list(Municipio.objects.filter(departamento_id=departamento_id)
                         .values('id', 'nombre', 'codigo'))
        return JsonResponse({'municipios': municipios})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_departamentos(request):
    """Vista para obtener todos los departamentos"""
    try:
        departamentos = list(Departamento.objects.values('id', 'nombre', 'codigo'))
        return JsonResponse({'departamentos': departamentos})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
