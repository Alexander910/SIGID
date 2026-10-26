## 2026-10-26 - IDOR in Views Bypassing DepartmentFilterMixin
**Vulnerability:** Views inheriting directly from `django.views.View` with manual `post` methods (like `AlertMarkReadView`) bypassed `DepartmentFilterMixin` logic, allowing non-admin users to modify resources belonging to other departments.
**Learning:** `DepartmentFilterMixin` only modifies `get_queryset()` for generic class-based views. Custom views handling HTTP methods manually directly with `get_object_or_404(Model, pk=pk)` will bypass queryset filtering unless explicitly passed a filtered queryset.
**Prevention:** Always construct a filtered queryset (e.g. `qs = Alert.objects.filter(product__department=request.user.department)` for non-admins) before calling `get_object_or_404(qs, pk=pk)` in manual view handlers.
