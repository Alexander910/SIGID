## 2025-05-15 - IDOR in Alert Mark Read
**Vulnerability:** Any authenticated user could mark any alert as read by sending a POST request to `/alertas/mark-read/<pk>/`, even if the alert belonged to a product in a different department.
**Learning:** Generic `View` classes (non-DRF and non-standard generic views like `UpdateView`) do not automatically benefit from `DepartmentFilterMixin`'s `get_queryset` override if the developer manually calls `get_object_or_404(Model, pk=pk)`.
**Prevention:** Always use a filtered queryset instead of the Model class directly when performing single-object lookups in views, especially in `post` methods or custom `View` subclasses.
