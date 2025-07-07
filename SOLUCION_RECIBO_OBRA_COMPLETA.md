# SOLUCIÓN APLICADA: Error en Creación de Recibos de Obra

## 🐛 **PROBLEMA IDENTIFICADO**

**Error Original:**
```
AttributeError at /recibos/crear-multiple/66/
Exception Value: property 'producto' of 'ReciboObra' object has no setter
```

**Causa:** 
- La vista `crear_recibo_multiple` en `recibos/views.py` (línea 759) intentaba crear un objeto `ReciboObra` pasando `producto=producto` como parámetro.
- Sin embargo, en el modelo `ReciboObra`, `producto` está definido como una `@property` (solo lectura), no como un campo de la base de datos.
- El modelo usa `DetalleReciboObra` para manejar múltiples productos por recibo.

## ✅ **SOLUCIÓN APLICADA**

### **Cambio 1: Corrección en `recibos/views.py`**
**Líneas 759-771** - Reemplazado:

**ANTES (❌ Incorrecto):**
```python
# Crear el recibo para este producto
recibo = ReciboObra.objects.create(
    pedido=pedido,
    cliente=pedido.cliente,
    producto=producto,  # ❌ Este campo no existe
    detalle_pedido=detalle,  # ❌ Este campo no existe
    cantidad_solicitada=cantidad,  # ❌ Este campo no existe
    notas_entrega=notas_generales,
    condicion_entrega=condicion_general,
    empleado=request.user
)
```

**DESPUÉS (✅ Correcto):**
```python
# Buscar un recibo existente para este pedido o crear uno nuevo
recibo, created = ReciboObra.objects.get_or_create(
    pedido=pedido,
    defaults={
        'cliente': pedido.cliente,
        'notas_entrega': notas_generales,
        'condicion_entrega': condicion_general,
        'empleado': request.user
    }
)

# Crear el detalle del recibo para este producto
DetalleReciboObra.objects.create(
    recibo=recibo,
    producto=producto,
    detalle_pedido=detalle,
    cantidad_solicitada=cantidad,
    estado='PENDIENTE'
)
```

### **Cambio 2: Ajuste en lógica de conteo**
**Líneas 786-800** - Ajustado el mensaje de éxito porque ahora creamos un recibo por pedido y agregamos productos como detalles.

## 🏗️ **ESTRUCTURA CORRECTA DEL MODELO**

```
ReciboObra (un recibo por pedido)
├── pedido (ForeignKey)
├── cliente (ForeignKey) 
├── fecha_entrega
├── notas_entrega
├── empleado (ForeignKey)
└── detalles (DetalleReciboObra) ← Múltiples productos aquí
    ├── producto (ForeignKey)
    ├── detalle_pedido (ForeignKey)
    ├── cantidad_solicitada
    └── estado
```

## 🧪 **PRUEBAS REALIZADAS**

1. ✅ **Verificación de permisos**: Usuario `Dalej` tiene permisos correctos
2. ✅ **Verificación de pedidos**: Hay 27 pedidos en estados válidos 
3. ✅ **Prueba de creación**: Script de prueba confirma que la corrección funciona
4. ✅ **Verificación de propiedades**: Las `@property` del modelo funcionan correctamente

## 🎯 **RESULTADO**

- ✅ **Error resuelto**: Ya no ocurre el `AttributeError`
- ✅ **Funcionalidad restaurada**: Los botones de "Crear Recibo de Obra" funcionan
- ✅ **Compatibilidad mantenida**: Las propiedades `producto`, `cantidad_solicitada`, etc. siguen funcionando
- ✅ **Estructura correcta**: Un recibo por pedido con múltiples detalles de productos

## 📍 **UBICACIÓN DE BOTONES**

Los botones de "Crear Recibo de Obra" aparecen en:
- **URL Admin**: `/panel/<pedido_id>/` (ej: `/panel/66/`)
- **Template**: `pedidos/templates/pedidos/detalle_pedido.html`
- **Condiciones**: Pedidos en estado `pagado`, `entregado`, `recibido`, `en_preparacion`, etc.
- **Permisos**: Solo usuarios con `is_staff=True` o `rol` en `['admin', 'recibos_obra']`

## ⚠️ **NOTA IMPORTANTE**

El error se debe a que estabas en el template de **cliente** (`detalle_mi_pedido.html`) que no tiene botones de recibo de obra (por diseño). Los botones están en el template de **administrador** (`detalle_pedido.html`).

**URLs correctas:**
- ❌ Cliente: `/panel/mis-pedidos/66/` (sin botones de recibo)
- ✅ Admin: `/panel/66/` (con botones de recibo)
