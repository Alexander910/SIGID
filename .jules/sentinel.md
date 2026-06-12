## 2025-05-15 - IDOR in Base View subclasses
**Vulnerability:** Insecure Direct Object Reference (IDOR) in views inheriting directly from `django.views.View`.
**Learning:** While the project uses `DepartmentFilterMixin` for generic views, custom `View` subclasses that override `post` or `get` and use `get_object_or_404(Model, pk=pk)` bypass the department-level isolation.
**Prevention:** In custom `View` methods, always define a filtered queryset that enforces authorization boundaries (e.g., `request.user.department`) before retrieving individual objects.
