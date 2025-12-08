from django.contrib import admin

from .models import (
    ActividadRegistrada,
    Cilindro,
    Nit,
    ReporteDiario,
    ReporteMensual,
    Trazabilidad,
)


@admin.register(Nit)
class NitAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "activo",
        "fecha_creacion",
        "creado_por",
    )
    search_fields = ("codigo",)
    list_filter = ("activo",)


@admin.register(Cilindro)
class CilindroAdmin(admin.ModelAdmin):
    list_display = (
        "numero_grabado",
        "nit",
        "estado_actual",
        "fecha_ingreso",
    )
    search_fields = (
        "numero_grabado",
        "nit__codigo",
    )
    list_filter = ("estado_actual",)
    readonly_fields = ("fecha_ingreso",)


@admin.register(Trazabilidad)
class TrazabilidadAdmin(admin.ModelAdmin):
    list_display = (
        "cilindro",
        "tipo_accion",
        "usuario",
        "fecha_hora",
    )
    list_filter = (
        "tipo_accion",
        "fecha_hora",
    )
    search_fields = (
        "cilindro__numero_grabado",
        "cilindro__nit__codigo",
    )
    readonly_fields = ("fecha_hora",)


@admin.register(ReporteDiario)
class ReporteDiarioAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "total_general",
    )
    ordering = ("-fecha",)


@admin.register(ActividadRegistrada)
class ActividadRegistradaAdmin(admin.ModelAdmin):
    list_display = (
        "reporte",
        "actividad",
        "cantidad",
    )
    ordering = ("actividad",)


@admin.register(ReporteMensual)
class ReporteMensualAdmin(admin.ModelAdmin):
    list_display = (
        "mes",
        "total_mes",
        "variacion_porcentual",
        "actividad_destacada",
    )
    ordering = ("-mes",)
