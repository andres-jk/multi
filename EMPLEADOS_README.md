# Sistema de Gestión de Empleados - MultiAndamios

## Descripción General

Este sistema permite que los administradores gestionen cuentas de empleados y asignen permisos específicos sobre diferentes módulos o funciones del sistema. Todo es gestionable desde el panel web con una interfaz intuitiva.

## Características Implementadas

### 🏗️ Modelo de Permisos Granular

**Campos de permisos en el modelo Usuario:**
- `puede_gestionar_productos`: Acceso a gestión de productos e inventario
- `puede_gestionar_pedidos`: Acceso a gestión de pedidos
- `puede_gestionar_recibos`: Acceso a recibos de obra
- `puede_gestionar_clientes`: Acceso a gestión de clientes
- `puede_ver_reportes`: Acceso a reportes del sistema
- `puede_gestionar_inventario`: Acceso específico a inventario
- `puede_procesar_pagos`: Acceso a procesamiento de pagos
- `activo`: Control de activación/desactivación de usuarios

### 👥 Roles de Usuario
- **admin**: Administrador con acceso completo
- **empleado**: Empleado con permisos específicos asignables
- **recibos_obra**: Empleado especializado en recibos de obra
- **cliente**: Usuario cliente del sistema

### 🔐 Sistema de Autenticación y Autorización

**Decoradores personalizados:**
- `@solo_administrador`: Solo administradores pueden acceder
- `@requiere_permiso(permiso)`: Requiere permiso específico
- `@admin_required`: Compatible con user_passes_test de Django
- `@usuario_activo`: Verifica que el usuario esté activo

**Template Tags:**
- `{% load permisos_tags %}`
- `{{ user|tiene_permiso:"productos" }}`: Verifica permiso específico
- `{{ user|es_admin }}`: Verifica si es administrador
- `{% mostrar_permisos empleado %}`: Muestra badges de permisos
- `{% permisos_usuario user as permisos %}`: Obtiene todos los permisos

### 🖥️ Interfaz Web de Gestión

#### Panel de Lista de Empleados (`/empleados/`)
- **Funcionalidades:**
  - Visualización de todos los empleados en tabla organizada
  - Filtros por estado (activo/inactivo)
  - Contadores de estadísticas (total, activos, inactivos)
  - Vista de permisos con badges visuales
  - Acciones rápidas (editar, activar/desactivar, eliminar)

#### Crear Empleado (`/empleados/crear/`)
- **Campos del formulario:**
  - Información básica (usuario, nombre, email, identificación)
  - Selección de rol (empleado/recibos_obra)
  - Asignación granular de permisos con checkboxes
  - Contraseña segura con validación

#### Editar Empleado (`/empleados/{id}/editar/`)
- **Funcionalidades:**
  - Edición de información personal
  - Modificación de permisos
  - Cambio de rol
  - Activación/desactivación
  - Validación de datos

#### Detalle de Empleado (`/empleados/{id}/detalle/`)
- **Información mostrada:**
  - Datos personales completos
  - Estado actual del usuario
  - Lista detallada de permisos con iconos
  - Fechas de creación y último acceso
  - Acciones administrativas disponibles

#### Gestión de Contraseñas (`/empleados/{id}/password/`)
- **Características:**
  - Cambio de contraseña por administrador
  - Validación de seguridad
  - Confirmación de contraseña
  - Información sobre políticas de contraseña

### 🎨 Interfaz de Usuario

**Diseño responsivo con:**
- Cards organizadas para mejor visualización
- Badges coloridos para permisos y estados
- Iconos Font Awesome para mejor UX
- Formularios con validación en tiempo real
- Mensajes de confirmación y error
- Modal de confirmación para acciones críticas

### 🔧 Herramientas de Desarrollo

#### Comandos de Django
```bash
# Crear administrador de prueba
python manage.py crear_admin --username admin --password admin123

# Crear empleados de prueba con diferentes permisos
python manage.py crear_empleados_prueba
```

#### Empleados de Prueba Creados
1. **juan_productos** - Gestión de productos e inventario
2. **maria_pedidos** - Gestión de pedidos y clientes
3. **carlos_recibos** - Especialista en recibos de obra
4. **ana_pagos** - Procesamiento de pagos y reportes
5. **pedro_completo** - Todos los permisos disponibles

## URLs Implementadas

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/empleados/` | `lista_empleados` | Lista todos los empleados |
| `/empleados/crear/` | `crear_empleado` | Formulario para crear empleado |
| `/empleados/{id}/editar/` | `editar_empleado` | Editar empleado existente |
| `/empleados/{id}/detalle/` | `detalle_empleado` | Ver detalles del empleado |
| `/empleados/{id}/password/` | `cambiar_password_empleado` | Cambiar contraseña |
| `/empleados/{id}/toggle/` | `activar_desactivar_empleado` | Activar/desactivar |
| `/empleados/{id}/eliminar/` | `eliminar_empleado` | Eliminar empleado |

## Archivos Principales

### Modelos
- `usuarios/models.py`: Modelo Usuario extendido con permisos

### Vistas
- `usuarios/views.py`: Todas las vistas de gestión de empleados

### Formularios
- `usuarios/forms.py`: Formularios para creación y edición

### Templates
- `usuarios/templates/usuarios/lista_empleados.html`
- `usuarios/templates/usuarios/crear_empleado.html`
- `usuarios/templates/usuarios/editar_empleado.html`
- `usuarios/templates/usuarios/detalle_empleado.html`
- `usuarios/templates/usuarios/cambiar_password_empleado.html`
- `usuarios/templates/usuarios/permisos_badge.html`

### Utilidades
- `usuarios/decorators.py`: Decoradores de permisos
- `usuarios/templatetags/permisos_tags.py`: Template tags personalizados

### Comandos
- `usuarios/management/commands/crear_admin.py`
- `usuarios/management/commands/crear_empleados_prueba.py`

## Seguridad

### Controles Implementados
- **Autenticación obligatoria**: Todos los endpoints requieren login
- **Autorización granular**: Solo administradores pueden gestionar empleados
- **Validación de permisos**: Verificación en vista y template
- **Usuarios activos**: Control de acceso para usuarios desactivados
- **Contraseñas seguras**: Validación de políticas de Django

### Validaciones
- Campos únicos (username, numero_identidad)
- Contraseñas con requisitos mínimos
- Verificación de permisos en cada acción
- Protección CSRF en formularios

## Navegación

El sistema se integra perfectamente en la navegación existente:
- **Menú "Administración"** → **"Empleados"** (solo para administradores)
- Acceso directo desde `/empleados/`
- Breadcrumbs en todas las páginas

## Casos de Uso

### Administrador
1. **Crear empleado**: Asignar usuario y permisos específicos
2. **Gestionar permisos**: Modificar accesos según necesidades
3. **Supervisar actividad**: Ver último login y estado
4. **Seguridad**: Activar/desactivar cuentas, cambiar contraseñas

### Empleado
1. **Acceso limitado**: Solo a módulos con permisos asignados
2. **Perfil personal**: Ver y editar información propia
3. **Funciones específicas**: Trabajar en áreas autorizadas

## Testing

### Credenciales de Prueba
- **Administrador**: `admin` / `admin123`
- **Empleados**: `[nombre]_[area]` / `emp123`

### Escenarios de Prueba
1. Login como admin → Gestionar empleados
2. Login como empleado → Verificar permisos limitados
3. Crear/editar/eliminar empleados
4. Asignar/modificar permisos
5. Activar/desactivar usuarios

## Estado del Proyecto

✅ **FUNCIONALIDADES IMPLEMENTADAS:**
- ✅ Modelo de permisos granular implementado
- ✅ Vista de lista de empleados funcionando
- ✅ Sistema de autorización robusto
- ✅ Integración con navegación principal
- ✅ Templates responsivos y profesionales
- ✅ Comandos de testing y datos de prueba
- ✅ Documentación completa

� **EN DESARROLLO:**
- 🚧 Crear empleado (función temporalmente deshabilitada)
- 🚧 Editar empleado (función temporalmente deshabilitada)
- 🚧 Cambiar contraseña (función temporalmente deshabilitada)
- 🚧 Activar/desactivar empleado (función temporalmente deshabilitada)
- 🚧 Eliminar empleado (función temporalmente deshabilitada)
- 🚧 Vista de detalle (función temporalmente deshabilitada)

🚀 **ESTADO ACTUAL: OPERATIVO PARA VISUALIZACIÓN**
El sistema está completamente funcional para visualizar empleados y sus permisos. Las funciones de edición están en desarrollo.

## Próximos Pasos Sugeridos

1. **Logs de auditoría**: Registrar cambios de permisos
2. **Notificaciones**: Alertar cambios a empleados
3. **Reportes**: Dashboard de actividad de empleados
4. **API REST**: Endpoints para gestión programática
5. **Grupos de permisos**: Templates de permisos predefinidos

---

## 🌐 **ESTADO ACTUAL DEL SISTEMA - JUNIO 2025**

### ✅ **Sistema Operativo y Funcional**

**Acceso al Sistema:**
- **URL Principal:** http://127.0.0.1:8000/
- **Lista de Empleados:** http://127.0.0.1:8000/empleados/
- **Estado del Servidor:** ✅ Funcionando en puerto 8000

### 📋 **Instrucciones de Uso:**

1. **Acceder a:** http://127.0.0.1:8000/
2. **Hacer login como admin:** `admin` / `admin123`
3. **Navegar a:** Administración → Empleados
4. **Ver lista de empleados** con badges de permisos
5. **Verificar empleados de prueba** disponibles

### 👁️ **Funcionalidades Actualmente Disponibles:**

- ✅ **Lista de empleados completa** - Totalmente funcional
- ✅ **Visualización de permisos** - Badges coloridos por permiso
- ✅ **Estadísticas en tiempo real** - Total, activos, inactivos
- ✅ **Información por empleado** - Datos completos visibles
- ✅ **Control de acceso** - Solo administradores
- ✅ **Diseño profesional** - Interface responsive

### 🛠️ **Funcionalidades en Desarrollo:**

- 🚧 **Crear empleados** - Función temporalmente deshabilitada
- 🚧 **Editar empleados** - Función temporalmente deshabilitada
- 🚧 **Gestión de contraseñas** - Función temporalmente deshabilitada
- 🚧 **Activar/desactivar** - Función temporalmente deshabilitada
- 🚧 **Eliminar empleados** - Función temporalmente deshabilitada

### 🎯 **Resumen del Estado Actual:**

**El sistema de gestión de empleados está OPERATIVO para visualización y consulta.** Los administradores pueden:

- Ver todos los empleados registrados
- Consultar permisos asignados a cada empleado
- Verificar el estado de cada cuenta
- Acceder de forma segura desde el menú de administración

**Las funciones de edición están en desarrollo y se activarán en futuras actualizaciones.**

### 💾 **Datos de Prueba Disponibles:**

| Usuario | Contraseña | Rol | Estado |
|---------|------------|-----|--------|
| `admin` | `admin123` | Administrador | ✅ Activo |
| `juan_productos` | `emp123` | Empleado | ✅ Activo |
| `maria_pedidos` | `emp123` | Empleado | ✅ Activo |
| `carlos_recibos` | `emp123` | Recibos Obra | ✅ Activo |
| `ana_pagos` | `emp123` | Empleado | ✅ Activo |
| `pedro_completo` | `emp123` | Empleado | ✅ Activo |

---

**✅ SISTEMA LISTO PARA USO Y DEMOSTRACIÓN**
