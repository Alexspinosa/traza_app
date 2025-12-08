from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Trazabilidad
from .servicies import registrar_actividad_en_reporte


@receiver(post_save, sender=Trazabilidad)
def crear_registro_en_reporte(sender, instance, created, **kwargs):
    if not created:
        return

    registrar_actividad_en_reporte(instance)
