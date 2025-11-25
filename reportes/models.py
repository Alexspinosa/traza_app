from django.db import models


# Create your models here.
class Registro(models.Model):
    fecha = models.DateTimeField()
    actividad = models.CharField(max_length=200)
    cantidad = models.IntegerField()

    def __str__(self):
        return f"{self.fecha} - {self.actividad} - {self.cantidad}"
