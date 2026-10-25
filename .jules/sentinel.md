## 2026-10-25 - IDOR in Manual View Handlers Bypassing Department Filter Mixins
**Vulnerability:** In `AlertMarkReadView`, a manual `post` implementation retrieved `Alert` instances directly via `get_object_or_404(Alert, pk=pk)` without checking department scope for non-admin users, leading to Insecure Direct Object Reference (IDOR).
**Learning:** Generic views inheriting base `View` and manually defining `post` methods do not automatically utilize `DepartmentFilterMixin` logic unless explicitly applied to the queryset within the view method.
**Prevention:** Always filter the model queryset by `request.user.department` (or relevant relationship path like `product__department`) before calling `get_object_or_404` in custom non-generic Django views.
