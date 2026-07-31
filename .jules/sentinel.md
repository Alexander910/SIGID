## 2026-07-31 - Bypass of DepartmentFilterMixin in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) on marking alerts as read, allowing any authenticated user to modify alerts of other departments.
**Learning:** Django views that inherit directly from `View` and implement manual `post` methods (like `AlertMarkReadView` in `alertas/views.py`) bypass the automatic `get_queryset` filtering of `DepartmentFilterMixin` because they retrieve objects using direct `get_object_or_404(Alert, pk=pk)` lookups.
**Prevention:** Implement explicit department-based filtering on object retrieval inside manual generic or basic `View` HTTP handlers, such as `get_object_or_404(Alert, pk=pk, product__department=request.user.department)` for non-admin users.
