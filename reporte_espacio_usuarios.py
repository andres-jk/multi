"""
ANÁLISIS DE ESPACIO POR REGISTRO DE USUARIO
Basado en el modelo Usuario encontrado en usuarios/models.py
"""

print("=" * 80)
print("ANÁLISIS DE ESPACIO POR REGISTRO DE USUARIO")
print("=" * 80)

print("\nBasado en el análisis del modelo usuarios.models.Usuario:")
print("- Hereda de AbstractUser (Django built-in)")
print("- Añade campos personalizados para roles y permisos")
print("- Se relaciona con Cliente y Direccion")

# 1. MODELO USUARIO (usuarios_usuario)
print("\n1. MODELO USUARIO (usuarios_usuario)")
print("-" * 50)

# Campos heredados de AbstractUser
campos_abstractuser = [
    ('id', 'BigAutoField', 8),
    ('password', 'CharField(128)', 128),
    ('last_login', 'DateTimeField', 19),
    ('is_superuser', 'BooleanField', 1),
    ('username', 'CharField(150)', 150),
    ('first_name', 'CharField(150)', 150),
    ('last_name', 'CharField(150)', 150),
    ('email', 'EmailField(254)', 254),
    ('is_staff', 'BooleanField', 1),
    ('is_active', 'BooleanField', 1),
    ('date_joined', 'DateTimeField', 19),
]

print("Campos heredados de AbstractUser:")
subtotal_abstract = 0
for campo, tipo, bytes_campo in campos_abstractuser:
    subtotal_abstract += bytes_campo
    print(f"  {campo:25} | {tipo:20} | {bytes_campo:>4} bytes")

print(f"\nSubtotal AbstractUser: {subtotal_abstract} bytes")

# Campos personalizados añadidos
campos_personalizados = [
    ('numero_identidad', 'CharField(20)', 20),
    ('rol', 'CharField(20)', 20),
    ('direccion_texto', 'CharField(255)', 255),
    ('puede_gestionar_productos', 'BooleanField', 1),
    ('puede_gestionar_pedidos', 'BooleanField', 1),
    ('puede_gestionar_recibos', 'BooleanField', 1),
    ('puede_gestionar_clientes', 'BooleanField', 1),
    ('puede_ver_reportes', 'BooleanField', 1),
    ('puede_gestionar_inventario', 'BooleanField', 1),
    ('puede_procesar_pagos', 'BooleanField', 1),
    ('activo', 'BooleanField', 1),
]

print("\nCampos personalizados:")
subtotal_custom = 0
for campo, tipo, bytes_campo in campos_personalizados:
    subtotal_custom += bytes_campo
    print(f"  {campo:25} | {tipo:20} | {bytes_campo:>4} bytes")

print(f"\nSubtotal campos personalizados: {subtotal_custom} bytes")

# Overhead de SQLite
overhead_sqlite = 16
total_usuario = subtotal_abstract + subtotal_custom + overhead_sqlite

print(f"\nOverhead SQLite (metadatos): {overhead_sqlite} bytes")
print("-" * 60)
print(f"TOTAL REGISTRO USUARIO: {total_usuario} bytes")

# 2. MODELO CLIENTE (usuarios_cliente)
print("\n\n2. MODELO CLIENTE (usuarios_cliente)")
print("-" * 50)
print("Relación OneToOne con Usuario")

campos_cliente = [
    ('id', 'BigAutoField', 8),
    ('usuario_id', 'OneToOneField', 8),
    ('telefono', 'CharField(50)', 50),
    ('direccion', 'CharField(255)', 255),
]

total_cliente = 0
for campo, tipo, bytes_campo in campos_cliente:
    total_cliente += bytes_campo
    print(f"  {campo:25} | {tipo:20} | {bytes_campo:>4} bytes")

total_cliente += overhead_sqlite
print(f"  {'SQLite overhead':25} | {'Metadata':20} | {overhead_sqlite:>4} bytes")
print("-" * 60)
print(f"TOTAL CLIENTE: {total_cliente} bytes")

# 3. MODELO DIRECCIÓN (usuarios_direccion)
print("\n\n3. MODELO DIRECCIÓN (usuarios_direccion)")
print("-" * 50)
print("Relación ForeignKey con Usuario (puede tener múltiples)")

campos_direccion = [
    ('id', 'BigAutoField', 8),
    ('usuario_id', 'ForeignKey', 8),
    ('calle', 'CharField(200)', 200),
    ('numero', 'CharField(20)', 20),
    ('complemento', 'CharField(200)', 200),
    ('departamento_id', 'ForeignKey', 8),
    ('municipio_id', 'ForeignKey', 8),
    ('codigo_divipola', 'CharField(5)', 5),
    ('codigo_postal', 'CharField(10)', 10),
    ('principal', 'BooleanField', 1),
]

total_direccion = 0
for campo, tipo, bytes_campo in campos_direccion:
    total_direccion += bytes_campo
    print(f"  {campo:25} | {tipo:20} | {bytes_campo:>4} bytes")

total_direccion += overhead_sqlite
print(f"  {'SQLite overhead':25} | {'Metadata':20} | {overhead_sqlite:>4} bytes")
print("-" * 60)
print(f"TOTAL POR DIRECCIÓN: {total_direccion} bytes")

# 4. CÁLCULO PARA UN USUARIO COMPLETO
print("\n\n4. ESPACIO TOTAL POR USUARIO COMPLETO")
print("=" * 50)

print("Escenarios típicos:")
print("\nESCENARIO 1: Usuario básico")
print("- 1 registro Usuario")
print("- 1 registro Cliente")
print("- 1 dirección")

escenario1 = total_usuario + total_cliente + total_direccion
print(f"Total: {escenario1} bytes ({escenario1/1024:.3f} KB)")

print("\nESCENARIO 2: Usuario con múltiples direcciones")
print("- 1 registro Usuario")
print("- 1 registro Cliente") 
print("- 2 direcciones (casa y trabajo)")

escenario2 = total_usuario + total_cliente + (total_direccion * 2)
print(f"Total: {escenario2} bytes ({escenario2/1024:.3f} KB)")

print("\nESCENARIO 3: Usuario solo con datos básicos")
print("- 1 registro Usuario")
print("- Sin cliente ni direcciones")

escenario3 = total_usuario
print(f"Total: {escenario3} bytes ({escenario3/1024:.3f} KB)")

# Usar el escenario 1 como promedio
promedio_por_usuario = escenario1

print(f"\n\nPROMEDIO ESTIMADO POR USUARIO: {promedio_por_usuario} bytes")

# 5. CONVERSIONES Y PROYECCIONES
print("\n\n5. CONVERSIONES Y PROYECCIONES")
print("=" * 50)

print(f"Espacio promedio por usuario:")
print(f"  • {promedio_por_usuario} bytes")
print(f"  • {promedio_por_usuario/1024:.3f} KB")
print(f"  • {promedio_por_usuario/(1024*1024):.6f} MB")

print(f"\nProyecciones para diferentes cantidades:")
cantidades = [10, 100, 500, 1000, 5000, 10000, 50000, 100000]

for cantidad in cantidades:
    total_bytes = promedio_por_usuario * cantidad
    
    if total_bytes < 1024:
        print(f"  {cantidad:>6} usuarios: {total_bytes:>10.0f} bytes")
    elif total_bytes < 1024 * 1024:
        print(f"  {cantidad:>6} usuarios: {total_bytes/1024:>10.2f} KB")
    elif total_bytes < 1024 * 1024 * 1024:
        print(f"  {cantidad:>6} usuarios: {total_bytes/(1024*1024):>10.2f} MB")
    else:
        print(f"  {cantidad:>6} usuarios: {total_bytes/(1024*1024*1024):>10.2f} GB")

# 6. MODELOS RELACIONADOS ADICIONALES
print("\n\n6. OTROS MODELOS RELACIONADOS (no incluidos en el cálculo principal)")
print("=" * 70)

print("\nMetodoPago (usuarios_metodopago):")
print("- Almacena información de pagos del usuario")
print("- Puede tener múltiples por usuario")
print("- Incluye campos como monto (DecimalField), tipo, estado, fechas")
print("- Archivos adjuntos (comprobantes) se almacenan en disco")
print("- Estimación: ~150-200 bytes por método de pago")

print("\nCarritoItem (usuarios_carritoitem):")
print("- Items temporales en el carrito de compras")
print("- Se limpian periódicamente")
print("- Estimación: ~50-80 bytes por item")

print("\n\n7. RESUMEN EJECUTIVO")
print("=" * 80)
print("CONCLUSIONES:")
print(f"  • Cada registro de usuario ocupa aproximadamente {promedio_por_usuario} bytes")
print(f"  • Esto equivale a {promedio_por_usuario/1024:.3f} KB por usuario")
print(f"  • Un sistema con 10,000 usuarios ocuparía ~{(promedio_por_usuario*10000)/(1024*1024):.1f} MB")
print(f"  • Un sistema con 100,000 usuarios ocuparía ~{(promedio_por_usuario*100000)/(1024*1024):.1f} MB")

print(f"\nEL CÁLCULO INCLUYE:")
print(f"  • Registro base de autenticación (AbstractUser)")
print(f"  • Campos personalizados de roles y permisos")
print(f"  • Perfil de cliente con datos de contacto")
print(f"  • Una dirección por usuario (promedio)")
print(f"  • Overhead de metadatos de SQLite")

print(f"\nNO INCLUYE:")
print(f"  • Archivos adjuntos (comprobantes de pago)")
print(f"  • Datos temporales (carritos)")
print(f"  • Logs o auditorías")
print(f"  • Índices de base de datos")

print(f"\nEn resumen: Cada usuario completo ocupa aproximadamente {promedio_por_usuario/1024:.2f} KB")
print("=" * 80)
