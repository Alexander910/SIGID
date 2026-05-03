"""
Modelos de Usuarios y Departamentos.
El departamento es el eje central del sistema —
todos los módulos dependen de él para filtrar datos.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    """Departamento / Área de la organización."""

    name = models.CharField('Nombre', max_length=100, unique=True)
    code = models.CharField('Código', max_length=20, unique=True)
    description = models.TextField('Descripción', blank=True)
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['name']

    def __str__(self):
        return f'{self.code} — {self.name}'


class User(AbstractUser):
    """Usuario del sistema con rol y departamento asignado."""

    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('encargado', 'Encargado de Área'),
    ]

    role = models.CharField(
        'Rol',
        max_length=20,
        choices=ROLE_CHOICES,
        default='encargado',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Departamento',
    )
    phone = models.CharField('Teléfono', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
