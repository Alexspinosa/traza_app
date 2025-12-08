from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localdate, now


# ============================================================
# REPORTE DIARIO
# ============================================================
class ReporteDiario(models.Model):
    fecha = models.DateField(
        default=now,
        unique=True
    )
    total_general = models.PositiveIntegerField(
        default=0,
        editable=False
    )

    if TYPE_CHECKING:
        actividades: models.Manager["ActividadRegistrada"]

    def calcular_total(self):
        total = sum(
            act.cantidad
            for act in self.actividades.all()
        )
        self.total_general = total
        self.save()
        return total

    def __str__(self):
        fecha_txt = self.fecha.strftime("%d/%m/%Y")
        return f"Reporte {fecha_txt} — Total: {self.total_general}"


# ============================================================
# ACTIVIDADES REGISTRADAS POR DÍA
# ============================================================
class ActividadRegistrada(models.Model):
    reporte = models.ForeignKey(
        ReporteDiario,
        related_name="actividades",
        on_delete=models.CASCADE
    )
    actividad = models.CharField(
        max_length=150
    )
    cantidad = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["actividad"]

    def __str__(self):
        return f"{self.actividad} ({self.cantidad})"


# ============================================================
# REPORTE MENSUAL
# ============================================================
class ReporteMensual(models.Model):
    mes = models.DateField(
        help_text="Guardar como día 1 del mes"
    )
    total_mes = models.PositiveIntegerField(
        default=0,
        editable=False
    )
    variacion_porcentual = models.FloatField(
        default=0,
        editable=False
    )
    actividad_destacada = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.mes.strftime("Reporte Mensual — %B %Y")


# ============================================================
# NIT DEL CILINDRO
# ============================================================
class Nit(models.Model):
    codigo = models.CharField(
        max_length=50,
        unique=True
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.codigo


# ============================================================
# CILINDRO
# ============================================================
class Cilindro(models.Model):
    ESTADOS = [
        ("RECIBIDO", "Recibido"),
        ("ETIQUETADO", "Etiquetado"),
        ("TRAZADO", "Trazado"),
        ("EN_PULIDOR", "En Pulidor"),
        ("EN_PINTOR", "En Pintor"),
    ]

    numero_grabado = models.CharField(
        max_length=100
    )
    nit = models.OneToOneField(
        Nit,
        on_delete=models.CASCADE
    )
    fecha_ingreso = models.DateField(
        auto_now_add=True
    )
    estado_actual = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="RECIBIDO"
    )
    observaciones = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.numero_grabado} - {self.nit.codigo}"


# ============================================================
# TRAZABILIDAD OPERATIVA
# ============================================================
class Trazabilidad(models.Model):
    ACCIONES = [
        ("TRAZADO", "Trazado"),
        ("ETIQUETADO", "Etiquetado"),
        ("NIT_CREADO", "NIT Creado"),
    ]

    cilindro = models.ForeignKey(
        Cilindro,
        on_delete=models.CASCADE,
        related_name="trazas"
    )
    tipo_accion = models.CharField(
        max_length=20,
        choices=ACCIONES
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    fecha_hora = models.DateTimeField(
        auto_now_add=True
    )
    comentario = models.TextField(
        blank=True,
        null=True
    )

    def clean(self):
        if self.tipo_accion == "TRAZADO":
            hoy = localdate()

            existe = Trazabilidad.objects.filter(
                cilindro=self.cilindro,
                tipo_accion="TRAZADO",
                fecha_hora__date=hoy,
            ).exists()

            if existe:
                raise ValidationError(
                    "Este cilindro ya fue trazado el día de hoy."
                )

    def save(self, *args, **kwargs):
        es_nuevo = self._state.adding
        self.full_clean()

        if self.tipo_accion == "ETIQUETADO":
            self.cilindro.estado_actual = "ETIQUETADO"

        elif self.tipo_accion == "TRAZADO":
            self.cilindro.estado_actual = "TRAZADO"

        elif self.tipo_accion == "NIT_CREADO":
            self.cilindro.estado_actual = "RECIBIDO"

        self.cilindro.save()
        super().save(*args, **kwargs)

        if not es_nuevo:
            return

        fecha_hoy = localdate()

        reporte, _ = ReporteDiario.objects.get_or_create(
            fecha=fecha_hoy
        )

        nombre_actividad = dict(self.ACCIONES).get(
            self.tipo_accion,
            self.tipo_accion,
        )

        actividad_obj, _ = ActividadRegistrada.objects.get_or_create(
            reporte=reporte,
            actividad=nombre_actividad,
            defaults={"cantidad": 0},
        )

        actividad_obj.cantidad = actividad_obj.cantidad + 1
        actividad_obj.save()

        reporte.calcular_total()

    def __str__(self):
        return f"{self.cilindro} - {self.tipo_accion}"
