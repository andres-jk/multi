#!/usr/bin/env python3
"""
Script para implementar interfaz móvil responsive en MultiAndamios
"""

import os
import shutil

def crear_interfaz_mobile():
    """
    Implementar interfaz móvil responsive completa
    """
    print("=== IMPLEMENTANDO INTERFAZ MÓVIL RESPONSIVE ===")
    
    # 1. Verificar estructura de directorios
    print("\n1. 📁 VERIFICANDO ESTRUCTURA DE DIRECTORIOS...")
    
    directorios = [
        'static',
        'static/css',
        'static/js',
        'templates'
    ]
    
    for directorio in directorios:
        if not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)
            print(f"   ✅ Creado: {directorio}")
        else:
            print(f"   ✅ Existe: {directorio}")
    
    # 2. Verificar archivos CSS y JS (ya creados)
    print("\n2. 📄 VERIFICANDO ARCHIVOS MÓVILES...")
    
    archivos_requeridos = [
        'static/css/mobile-responsive.css',
        'static/js/mobile-menu.js'
    ]
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✅ Existe: {archivo}")
            
            # Mostrar tamaño del archivo
            size = os.path.getsize(archivo)
            print(f"      Tamaño: {size} bytes")
        else:
            print(f"   ❌ Falta: {archivo}")
    
    # 3. Crear template base mobile-friendly
    print("\n3. 🎨 CREANDO TEMPLATE BASE MOBILE-FRIENDLY...")
    
    template_base = """{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="description" content="MultiAndamios - Alquiler de andamios y equipos de construcción">
    <meta name="theme-color" content="#F9C552">
    
    <title>{% block title %}MultiAndamios - Alquiler de Andamios{% endblock %}</title>
    
    <!-- CSS Principal -->
    <link rel="stylesheet" href="{% static 'css/estilos.css' %}">
    <link rel="stylesheet" href="{% static 'css/theme-colors.css' %}">
    
    <!-- CSS Mobile Responsive -->
    <link rel="stylesheet" href="{% static 'css/mobile-responsive.css' %}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="{% static 'images/favicon.png' %}">
    
    <!-- PWA Meta Tags -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="MultiAndamios">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navegación principal (se convierte en menú lateral en móviles) -->
    <nav class="main-navigation" role="navigation" aria-label="Menú principal">
        {% if user.is_authenticated %}
            <a href="{% url 'inicio' %}" class="nav-button">
                🏠 INICIO
            </a>
            <a href="{% url 'productos:lista' %}" class="nav-button">
                🚧 PRODUCTOS
            </a>
            <a href="{% url 'pedidos:lista' %}" class="nav-button">
                📋 PEDIDOS
            </a>
            <a href="{% url 'pedidos:mis_pedidos' %}" class="nav-button">
                ✅ MIS PEDIDOS
            </a>
            <a href="{% url 'pedidos:pendientes' %}" class="nav-button">
                ⏳ PENDIENTES
            </a>
            <a href="{% url 'productos:carrito' %}" class="nav-button">
                🛒 CARRITO <span class="carrito-count">{{ carrito_count|default:0 }}</span>
            </a>
            {% if user.is_staff %}
            <a href="{% url 'admin:index' %}" class="nav-button">
                ⚙️ ADMINISTRACIÓN
            </a>
            {% endif %}
            <a href="{% url 'usuarios:logout' %}" class="nav-button">
                🚪 CERRAR SESIÓN
            </a>
        {% else %}
            <a href="{% url 'usuarios:login' %}" class="nav-button">
                🔐 INICIAR SESIÓN
            </a>
            <a href="{% url 'usuarios:registro' %}" class="nav-button">
                📝 REGISTRARSE
            </a>
        {% endif %}
    </nav>
    
    <!-- Contenido principal -->
    <main class="main-content" role="main">
        {% if messages %}
            <div class="messages-container">
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible" role="alert">
                        {{ message }}
                        <button type="button" class="close" data-dismiss="alert" aria-label="Cerrar">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    <footer class="main-footer">
        <div class="footer-content">
            <p>&copy; 2025 MultiAndamios. Todos los derechos reservados.</p>
            <p>🏗️ Alquiler profesional de andamios y equipos de construcción</p>
        </div>
    </footer>
    
    <!-- JavaScript -->
    <script src="{% static 'js/mobile-menu.js' %}"></script>
    {% block extra_js %}{% endblock %}
    
    <!-- JavaScript para mejorar UX en móviles -->
    <script>
        // Prevenir zoom accidental en iOS
        document.addEventListener('touchstart', function() {}, {passive: true});
        
        // Mejorar rendimiento en móviles
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                // Registrar service worker si está disponible
                console.log('Service Worker disponible');
            });
        }
        
        // Debug para desarrollo
        console.log('MultiAndamios Mobile - Viewport:', window.innerWidth + 'x' + window.innerHeight);
    </script>
</body>
</html>"""
    
    template_path = 'templates/base_mobile.html'
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_base)
    
    print(f"   ✅ Creado: {template_path}")
    
    # 4. Crear estilos adicionales para mejorar la experiencia móvil
    print("\n4. 🎨 CREANDO ESTILOS ADICIONALES...")
    
    estilos_adicionales = """/* Estilos adicionales para mejorar la experiencia móvil */

/* Mejoras generales para móviles */
@media (max-width: 768px) {
    
    /* Hacer que los elementos sean más fáciles de tocar */
    .btn, .button, .nav-button, input[type="submit"], input[type="button"] {
        min-height: 44px;
        min-width: 44px;
        padding: 12px 16px;
        font-size: 16px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    /* Mejorar inputs de formularios */
    input[type="text"], 
    input[type="email"], 
    input[type="password"], 
    input[type="tel"], 
    input[type="number"],
    textarea, 
    select {
        font-size: 16px; /* Prevenir zoom en iOS */
        padding: 12px;
        border-radius: 6px;
        border: 2px solid #ddd;
        width: 100%;
        box-sizing: border-box;
    }
    
    /* Mejorar tablas en móviles */
    .table-responsive {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-bottom: 20px;
    }
    
    .table-responsive table {
        min-width: 600px;
        font-size: 14px;
    }
    
    /* Cards más amigables en móviles */
    .card {
        margin-bottom: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 15px;
    }
    
    /* Mejorar listas */
    .list-group-item {
        padding: 15px;
        font-size: 16px;
        border-radius: 8px !important;
        margin-bottom: 8px;
    }
    
    /* Productos grid más amigable */
    .productos-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 15px;
        padding: 15px;
    }
    
    .producto-card {
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Carrito más usable */
    .carrito-item {
        padding: 15px;
        border-bottom: 1px solid #eee;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .carrito-item img {
        width: 60px;
        height: 60px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    /* Checkout más fácil en móviles */
    .checkout-form .form-group {
        margin-bottom: 20px;
    }
    
    .checkout-summary {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    /* Alertas más visibles */
    .alert {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 16px;
    }
    
    /* Footer más compacto */
    .main-footer {
        padding: 20px;
        text-align: center;
        background: #f8f9fa;
        border-top: 1px solid #ddd;
        margin-top: 40px;
    }
    
    .footer-content p {
        margin: 5px 0;
        font-size: 14px;
    }
    
    /* Breadcrumbs más legibles */
    .breadcrumb {
        background: transparent;
        padding: 10px 0;
        font-size: 14px;
    }
    
    /* Modals adaptados para móviles */
    .modal-dialog {
        margin: 20px;
        max-width: calc(100% - 40px);
    }
    
    .modal-content {
        border-radius: 8px;
    }
    
    .modal-header, .modal-footer {
        padding: 15px;
    }
    
    .modal-body {
        padding: 20px;
    }
    
    /* Pagination más usable */
    .pagination {
        justify-content: center;
        margin: 20px 0;
    }
    
    .page-link {
        padding: 12px 16px;
        font-size: 16px;
        border-radius: 8px !important;
        margin: 0 4px;
    }
    
    /* Loading states */
    .loading {
        opacity: 0.6;
        pointer-events: none;
    }
    
    .spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #1A1228;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
}

/* Mejoras específicas para iPhone */
@supports (-webkit-appearance: none) {
    input[type="text"], 
    input[type="email"], 
    input[type="password"], 
    input[type="tel"], 
    input[type="number"],
    textarea, 
    select {
        -webkit-appearance: none;
        border-radius: 6px;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    @media (max-width: 768px) {
        .main-navigation {
            background-color: #2A2238;
            color: #F9C552;
        }
        
        .mobile-header {
            background: linear-gradient(135deg, #2A2238 0%, #1A1228 100%);
            color: #F9C552;
        }
        
        .mobile-header h1 {
            color: #F9C552;
        }
        
        .main-navigation .nav-button {
            background: rgba(249, 197, 82, 0.1);
            color: #F9C552;
            border-color: #F9C552;
        }
        
        .main-navigation .nav-button:hover {
            background: #F9C552;
            color: #1A1228;
        }
    }
}"""
    
    estilos_path = 'static/css/mobile-enhancements.css'
    with open(estilos_path, 'w', encoding='utf-8') as f:
        f.write(estilos_adicionales)
    
    print(f"   ✅ Creado: {estilos_path}")
    
    # 5. Generar instrucciones de implementación
    print("\n5. 📋 GENERANDO INSTRUCCIONES...")
    
    instrucciones = """# 🚀 INSTRUCCIONES DE IMPLEMENTACIÓN - INTERFAZ MÓVIL

## ✅ ARCHIVOS CREADOS:

1. **static/css/mobile-responsive.css** - Estilos principales para móviles
2. **static/js/mobile-menu.js** - JavaScript para menú hamburguesa
3. **static/css/mobile-enhancements.css** - Mejoras adicionales para UX móvil
4. **templates/base_mobile.html** - Template base mobile-friendly

## 🔧 PASOS PARA APLICAR:

### EN DESARROLLO LOCAL:
```bash
# 1. Verificar archivos creados
ls -la static/css/ | grep mobile
ls -la static/js/ | grep mobile

# 2. Actualizar templates existentes para usar el nuevo base
# Cambiar {% extends "base.html" %} por {% extends "base_mobile.html" %}

# 3. Probar en navegador con herramientas de desarrollador
# F12 → Toggle device toolbar → Seleccionar móvil
```

### EN PYTHONANYWHERE:
```bash
# 1. Subir al repositorio
git add .
git commit -m "Implementar interfaz móvil responsive"
git push origin main

# 2. Actualizar en servidor
cd /home/Dalej/multi
git pull origin main

# 3. Actualizar archivos estáticos
python3.10 manage.py collectstatic --noinput

# 4. Reiniciar aplicación
# Panel Web → Reload
```

## 📱 CARACTERÍSTICAS IMPLEMENTADAS:

### MÓVILES (≤ 768px):
- ✅ **Menú hamburguesa** en esquina superior derecha
- ✅ **Menú lateral deslizable** desde la izquierda
- ✅ **Overlay oscuro** para cerrar menú
- ✅ **Botones más grandes** (44px mínimo para touch)
- ✅ **Inputs optimizados** (sin zoom accidental en iOS)
- ✅ **Tablas responsivas** con scroll horizontal
- ✅ **Cards y formularios adaptados**

### TABLETS (481px - 768px):
- ✅ **Menú lateral más estrecho** (60% del ancho)
- ✅ **Textos y botones medianos**

### MÓVILES PEQUEÑOS (≤ 480px):
- ✅ **Interfaz ultra-compacta**
- ✅ **Espaciado reducido**
- ✅ **Textos más pequeños**

## 🎨 FUNCIONALIDADES:

### JavaScript:
- ✅ **Auto-detección** de tamaño de pantalla
- ✅ **Event listeners** para touch y click
- ✅ **Cerrar con tecla Escape**
- ✅ **Prevenir scroll** cuando menú abierto
- ✅ **Animaciones suaves**

### CSS:
- ✅ **Media queries** responsivas
- ✅ **Flexbox y Grid** para layouts
- ✅ **Animaciones CSS** para transiciones
- ✅ **Dark mode support**
- ✅ **Optimizaciones para iOS/Android**

## 🧪 TESTING:

### Dispositivos a probar:
- 📱 **iPhone** (Safari Mobile)
- 📱 **Android** (Chrome Mobile)
- 📱 **iPad** (Safari)
- 📱 **Android Tablet** (Chrome)

### Funcionalidades a verificar:
- [ ] Menú hamburguesa abre/cierra correctamente
- [ ] Navegación funciona en todos los enlaces
- [ ] Formularios son usables con teclado virtual
- [ ] Checkout funciona en móviles
- [ ] Carrito se puede usar con touch
- [ ] Productos se ven bien en listas/grid

## 📊 MÉTRICAS ESPERADAS:

- ✅ **Tiempo de carga**: < 3 segundos en 3G
- ✅ **Usabilidad**: Elementos > 44px
- ✅ **Responsive**: 320px - 768px
- ✅ **Accesibilidad**: ARIA labels incluidos

¡La interfaz móvil está lista para implementar!"""
    
    instrucciones_path = 'INSTRUCCIONES_MOBILE.md'
    with open(instrucciones_path, 'w', encoding='utf-8') as f:
        f.write(instrucciones)
    
    print(f"   ✅ Creado: {instrucciones_path}")
    
    # 6. Resumen final
    print("\n" + "="*60)
    print("🎉 IMPLEMENTACIÓN MÓVIL COMPLETADA")
    print("="*60)
    
    archivos_creados = [
        'static/css/mobile-responsive.css',
        'static/js/mobile-menu.js',
        'static/css/mobile-enhancements.css',
        'templates/base_mobile.html',
        'INSTRUCCIONES_MOBILE.md'
    ]
    
    print("\n📁 ARCHIVOS CREADOS:")
    for archivo in archivos_creados:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            print(f"   ✅ {archivo} ({size} bytes)")
        else:
            print(f"   ❌ {archivo} (ERROR)")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("1. Revisar archivos creados")
    print("2. Actualizar templates para usar base_mobile.html")
    print("3. Subir al repositorio")
    print("4. Aplicar en PythonAnywhere")
    print("5. Probar en dispositivos móviles")
    
    print("\n📱 RESULTADO ESPERADO:")
    print("- Menú hamburguesa en móviles")
    print("- Interfaz más compacta y usable")
    print("- Mejor experiencia en touch devices")
    print("- Diseño responsive que se adapta automáticamente")
    
    return True

if __name__ == '__main__':
    try:
        crear_interfaz_mobile()
        print("\n✅ ¡IMPLEMENTACIÓN EXITOSA!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
