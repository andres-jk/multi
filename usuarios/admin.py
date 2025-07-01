from django.contrib import admin
from django.utils import timezone
from django.contrib.admin import SimpleListFilter
from .models import Usuario, Cliente, Direccion, CarritoItem, MetodoPago
from .models_divipola import Departamento, Municipio
from .utils import enviar_correo_pago
from .forms import UsuarioAdminCreationForm, UsuarioAdminChangeForm

class EstadoUsuarioFilter(SimpleListFilter):
    title = 'Estado del Usuario'
    parameter_name = 'estado_usuario'

    def lookups(self, request, model_admin):
        return (
            ('activo', 'Activos'),
            ('inactivo', 'Inactivos'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'activo':
            return queryset.filter(usuario__is_active=True)
        if self.value() == 'inactivo':
            return queryset.filter(usuario__is_active=False)
        return queryset

class RolUsuarioFilter(SimpleListFilter):
    title = 'Rol del Usuario'
    parameter_name = 'rol_usuario'

    def lookups(self, request, model_admin):
        return Usuario.ROLES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(usuario__rol=self.value())
        return queryset

class ClienteInline(admin.StackedInline):
    model = Cliente
    can_delete = False
    verbose_name_plural = 'Datos de Cliente'
    max_num = 1

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    add_form = UsuarioAdminCreationForm
    form = UsuarioAdminChangeForm
    
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    list_display = ('username', 'first_name', 'last_name', 'email', 'rol')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'numero_identidad')
    list_filter = ('rol', 'is_active', EstadoUsuarioFilter, RolUsuarioFilter)
    inlines = [ClienteInline]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'numero_identidad')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
        ('Rol', {'fields': ('rol',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'password2', 'first_name', 'last_name', 'email', 'numero_identidad', 'rol')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not hasattr(obj, 'cliente'):
            Cliente.objects.create(usuario=obj)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    list_display = ('usuario', 'get_numero_identidad', 'telefono', 'get_estado_usuario')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'usuario__numero_identidad')
    list_filter = (EstadoUsuarioFilter, RolUsuarioFilter)

    def get_numero_identidad(self, obj):
        return obj.usuario.numero_identidad
    get_numero_identidad.short_description = 'Número de Identidad'
    
    def get_estado_usuario(self, obj):
        return 'Activo' if obj.usuario.is_active else 'Inactivo'
    get_estado_usuario.short_description = 'Estado'
    get_estado_usuario.admin_order_field = 'usuario__is_active'

@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/admin_custom.css',)
        }
    
    list_display = ('usuario', 'producto', 'cantidad', 'dias_renta', 'fecha_agregado')
    list_filter = ('fecha_agregado', 'reservado')
    search_fields = ('usuario__username', 'producto__nombre')
    raw_id_fields = ['usuario', 'producto']
    readonly_fields = ('fecha_agregado',)

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'calle', 'municipio', 'departamento', 'principal')
    list_filter = ('departamento', 'municipio', 'principal')
    search_fields = ('usuario__username', 'calle', 'municipio__nombre', 'departamento__nombre')
    raw_id_fields = ['usuario', 'departamento', 'municipio']

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'tipo', 'usuario', 'monto', 'estado', 'fecha_pago', 'fecha_verificacion', 'dias_pendiente')
    list_filter = ('tipo', 'estado', 'fecha_pago', 'fecha_verificacion')
    search_fields = ('usuario__username', 'pedido__id_pedido', 'numero_referencia')
    readonly_fields = ('fecha_creacion', 'fecha_pago', 'fecha_verificacion')
    raw_id_fields = ['usuario', 'pedido', 'verificado_por']
    actions = ['aprobar_pagos', 'rechazar_pagos']

    def dias_pendiente(self, obj):
        if obj.estado == 'pendiente' and not obj.fecha_verificacion:
            return (timezone.now() - obj.fecha_creacion).days
        return '-'
    dias_pendiente.short_description = 'Días Pendiente'

    def aprobar_pagos(self, request, queryset):
        for pago in queryset.filter(estado='pendiente'):
            pago.estado = 'aprobado'
            pago.verificado_por = request.user
            pago.fecha_verificacion = timezone.now()
            pago.fecha_pago = timezone.now()
            pago.save()
            
            # Enviar correo de confirmación
            enviar_correo_pago(pago.pedido, 'aprobado')
            
        self.message_user(request, f'Se aprobaron {queryset.count()} pagos exitosamente.')
    aprobar_pagos.short_description = 'Aprobar pagos seleccionados'

    def rechazar_pagos(self, request, queryset):
        for pago in queryset.filter(estado='pendiente'):
            pago.estado = 'rechazado'
            pago.verificado_por = request.user
            pago.fecha_verificacion = timezone.now()
            pago.save()
            
            # Enviar correo de rechazo
            enviar_correo_pago(pago.pedido, 'rechazado')
            
        self.message_user(request, f'Se rechazaron {queryset.count()} pagos.')
    rechazar_pagos.short_description = 'Rechazar pagos seleccionados'

    def save_model(self, request, obj, form, change):
        if 'estado' in form.changed_data:
            obj.verificado_por = request.user
            obj.fecha_verificacion = timezone.now()
            if obj.estado == 'aprobado':
                obj.fecha_pago = timezone.now()
                # Enviar correo de confirmación
                enviar_correo_pago(obj.pedido, 'aprobado')
            elif obj.estado == 'rechazado':
                # Enviar correo de rechazo
                enviar_correo_pago(obj.pedido, 'rechazado')
        super().save_model(request, obj, form, change)

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')
    ordering = ('nombre',)

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'departamento', 'codigo', 'costo_transporte')
    list_filter = ('departamento',)
    search_fields = ('nombre', 'codigo', 'departamento__nombre')
    raw_id_fields = ['departamento']
    list_editable = ['costo_transporte']
