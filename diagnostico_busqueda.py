#!/usr/bin/env python
"""
Script de diagnóstico completo para la funcionalidad de búsqueda
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiandamios.settings')
sys.path.append('.')
django.setup()

def diagnostico_completo():
    """Realiza un diagnóstico completo del sistema"""
    
    print("=== DIAGNÓSTICO COMPLETO DEL SISTEMA ===\n")
    
    # 1. Verificar importaciones
    print("1. Verificando importaciones...")
    try:
        from django.db.models import Q
        from usuarios.models import Usuario
        from pedidos.models import Cliente
        from pedidos.views import lista_clientes
        print("✓ Todas las importaciones correctas")
    except Exception as e:
        print(f"✗ Error en importaciones: {e}")
        return
    
    # 2. Verificar base de datos
    print("\n2. Verificando base de datos...")
    try:
        usuarios_count = Usuario.objects.count()
        clientes_count = Cliente.objects.count()
        print(f"✓ Usuarios: {usuarios_count}")
        print(f"✓ Clientes: {clientes_count}")
    except Exception as e:
        print(f"✗ Error en base de datos: {e}")
        return
    
    # 3. Verificar que existan datos
    print("\n3. Verificando datos existentes...")
    clientes = Cliente.objects.select_related('usuario').all()
    
    if clientes.exists():
        print(f"✓ Encontrados {clientes.count()} clientes")
        for i, cliente in enumerate(clientes[:3]):  # Mostrar solo los primeros 3
            print(f"   {i+1}. {cliente.usuario.numero_identidad} - {cliente.usuario.first_name} {cliente.usuario.last_name}")
    else:
        print("⚠ No hay clientes en la base de datos")
    
    # 4. Probar la función de búsqueda
    print("\n4. Probando función de búsqueda...")
    
    if clientes.exists():
        cliente_prueba = clientes.first()
        busqueda_test = cliente_prueba.usuario.numero_identidad
        
        print(f"   Buscando: '{busqueda_test}'")
        
        # Aplicar el mismo filtro que en la vista
        resultados = clientes.filter(
            Q(usuario__numero_identidad__icontains=busqueda_test) |
            Q(usuario__first_name__icontains=busqueda_test) |
            Q(usuario__last_name__icontains=busqueda_test) |
            Q(usuario__username__icontains=busqueda_test) |
            Q(usuario__email__icontains=busqueda_test) |
            Q(usuario__telefono__icontains=busqueda_test) |
            Q(direccion__icontains=busqueda_test)
        )
        
        print(f"   Resultados: {resultados.count()}")
        
        if resultados.exists():
            print("✓ Función de búsqueda funciona correctamente")
        else:
            print("✗ Función de búsqueda no encuentra resultados")
    else:
        print("⚠ No se puede probar búsqueda sin datos")
    
    # 5. Verificar estructura de usuario
    print("\n5. Verificando estructura de usuario...")
    if clientes.exists():
        cliente_test = clientes.first()
        usuario_test = cliente_test.usuario
        
        print(f"   Usuario: {usuario_test.username}")
        print(f"   Número identidad: {usuario_test.numero_identidad}")
        print(f"   Nombre: {usuario_test.first_name}")
        print(f"   Apellido: {usuario_test.last_name}")
        print(f"   Email: {usuario_test.email}")
        print(f"   Teléfono: {getattr(usuario_test, 'telefono', 'N/A')}")
        print(f"   Dirección (cliente): {cliente_test.direccion}")
        print(f"   Rol: {usuario_test.rol}")
        print(f"   Es staff: {usuario_test.is_staff}")
        print("✓ Estructura de usuario verificada")
    
    # 6. Verificar URLs
    print("\n6. Verificando configuración de URLs...")
    try:
        from django.urls import reverse
        url_lista_clientes = reverse('pedidos:lista_clientes')
        print(f"✓ URL lista_clientes: {url_lista_clientes}")
    except Exception as e:
        print(f"✗ Error en URLs: {e}")
    
    # 7. Verificar vista directamente
    print("\n7. Probando vista directamente...")
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        
        factory = RequestFactory()
        request = factory.get('/pedidos/admin/clientes/')
        
        # Crear un usuario staff para la prueba
        usuario_staff = Usuario.objects.filter(is_staff=True).first()
        if not usuario_staff:
            usuario_staff = Usuario.objects.create_user(
                username='staff_test',
                password='test123',
                is_staff=True,
                rol='admin'
            )
        
        request.user = usuario_staff
        
        # Intentar llamar a la vista
        response = lista_clientes(request)
        print(f"✓ Vista ejecutada correctamente, status: {response.status_code}")
        
        # Probar con parámetros de búsqueda
        request_search = factory.get('/pedidos/admin/clientes/?busqueda_identidad=12345')
        request_search.user = usuario_staff
        
        response_search = lista_clientes(request_search)
        print(f"✓ Vista con búsqueda ejecutada, status: {response_search.status_code}")
        
    except Exception as e:
        print(f"✗ Error en vista: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== DIAGNÓSTICO COMPLETADO ===")

if __name__ == '__main__':
    diagnostico_completo()
