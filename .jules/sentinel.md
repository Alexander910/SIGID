## 2026-11-10 - IDOR in AlertMarkReadView
**Vulnerability:** In `AlertMarkReadView`, any authenticated user could mark alerts belonging to another department as read by submitting a POST request with the alert ID (`get_object_or_404(Alert, pk=pk)` without department validation).
**Learning:** Generic Django views inheriting directly from base `View` and handling manual POST endpoints do not use `DepartmentFilterMixin`, and direct model lookups by ID bypass tenant/department isolation logic.
**Prevention:** In custom `View` classes, filter the queryset by `product__department=request.user.department` for non-admin users before retrieving objects with `get_object_or_404`.
