## 2026-11-01 - IDOR in AlertMarkReadView
**Vulnerability:** AlertMarkReadView allowed users with the 'encargado' role to mark alerts as read for products belonging to any department via direct primary key POST requests.
**Learning:** Django views inheriting directly from base `View` and writing custom `post()` methods do not automatically utilize `DepartmentFilterMixin` logic, leading to unconstrained object lookup (`get_object_or_404(Alert, pk=pk)`).
**Prevention:** Always scope the queryset by `product__department=request.user.department` for non-admin users before calling `get_object_or_404` in custom `View` endpoints.
