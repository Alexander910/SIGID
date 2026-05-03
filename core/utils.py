"""
Utilidades generales del sistema SIGID.
"""
import csv
from django.http import HttpResponse


def export_to_csv(queryset, filename, fields):
    """
    Exporta un queryset a un archivo CSV descargable.

    Args:
        queryset: Django queryset a exportar.
        filename: Nombre del archivo (sin extensión).
        fields: Lista de tuplas (nombre_campo, etiqueta).

    Returns:
        HttpResponse con el CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

    writer = csv.writer(response)

    # Encabezados
    writer.writerow([label for _, label in fields])

    # Datos
    for obj in queryset:
        row = []
        for field_name, _ in fields:
            value = obj
            for attr in field_name.split('__'):
                value = getattr(value, attr, '')
            if callable(value):
                value = value()
            row.append(str(value))
        writer.writerow(row)

    return response
