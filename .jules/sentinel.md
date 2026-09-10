## 2026-09-10 - IDOR Bypass in Manual POST Views Not Using DepartmentFilterMixin
**Vulnerability:** `AlertMarkReadView` directly called `get_object_or_404(Alert, pk=pk)` without checking whether the requested alert belonged to the user's department, enabling cross-department IDOR data modification.
**Learning:** `DepartmentFilterMixin` only automatically overrides `get_queryset()` for generic class-based views. Custom views inheriting directly from `django.views.View` that handle POST requests manually bypass `DepartmentFilterMixin` logic unless explicitly filtered.
**Prevention:** Always construct a department-filtered queryset (`qs.filter(product__department=request.user.department)`) before calling `get_object_or_404()` in custom `View` POST handlers for non-admin users.
