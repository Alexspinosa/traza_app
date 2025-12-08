from datetime import timedelta
from typing import Optional

from django.utils.timezone import localdate

from .models import (
    ActividadRegistrada,
    ReporteDiario,
    ReporteMensual,
)


def registrar_actividad_en_reporte(traza) -> None:
    fecha_hoy = localdate()

    reporte, _ = ReporteDiario.objects.get_or_create(
        fecha=fecha_hoy,
    )

    nombre_actividad = dict(traza.ACCIONES).get(
        traza.tipo_accion,
        traza.tipo_accion,
    )

    actividad, _ = ActividadRegistrada.objects.get_or_create(
        reporte=reporte,
        actividad=nombre_actividad,
        defaults={"cantidad": 0},
    )

    actividad.cantidad = actividad.cantidad + 1
    actividad.save()

    calcular_total_reporte_diario(reporte)


def calcular_total_reporte_diario(
    reporte: ReporteDiario,
) -> None:
    total = sum(
        act.cantidad
        for act in reporte.actividades.all()
    )
    reporte.total_general = total
    reporte.save()


def calcular_reporte_mensual(
    reporte_mensual: ReporteMensual,
) -> None:
    inicio_mes = reporte_mensual.mes.replace(day=1)
    fin_mes = inicio_mes + timedelta(days=31)

    reportes = ReporteDiario.objects.filter(
        fecha__range=(inicio_mes, fin_mes),
    )

    total = sum(r.total_general for r in reportes)
    reporte_mensual.total_mes = total

    actividades = ActividadRegistrada.objects.filter(
        reporte__fecha__range=(inicio_mes, fin_mes),
    )

    conteo: dict[str, int] = {}

    for act in actividades:
        nombre: str = act.actividad
        cantidad: int = act.cantidad
        conteo[nombre] = conteo.get(nombre, 0) + cantidad

    actividad_destacada: Optional[str] = None

    if len(conteo) > 0:
        actividad_destacada = max(
            conteo.items(),
            key=lambda item: item[1],
        )[0]

    reporte_mensual.actividad_destacada = actividad_destacada

    mes_anterior = inicio_mes - timedelta(days=1)
    mes_anterior = mes_anterior.replace(day=1)

    previo = ReporteMensual.objects.filter(
        mes=mes_anterior,
    ).first()

    if previo and previo.total_mes > 0:
        diferencia = total - previo.total_mes
        reporte_mensual.variacion_porcentual = (
            diferencia / previo.total_mes
        ) * 100
    else:
        reporte_mensual.variacion_porcentual = 0

    reporte_mensual.save()
