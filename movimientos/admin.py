from django.contrib import admin
from .models import Movement


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'type', 'quantity', 'user', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('product__name', 'product__code')
    readonly_fields = ('created_at',)
