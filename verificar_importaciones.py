#!/usr/bin/env python3
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
django.setup()

try:
    from usuarios.forms import EmpleadoForm
    print('✅ EmpleadoForm se importa correctamente')
except ImportError as e:
    print(f'❌ Error al importar EmpleadoForm: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Error general: {e}')
    exit(1)

try:
    from usuarios.views_empleados import lista_empleados
    print('✅ Vistas de empleados cargadas correctamente')
except ImportError as e:
    print(f'❌ Error al importar vistas de empleados: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Error general en vistas: {e}')
    exit(1)

print('✅ Todas las verificaciones pasaron exitosamente')
