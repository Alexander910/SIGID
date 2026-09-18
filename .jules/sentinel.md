## 2026-09-18 - Manual View IDOR Pattern in Non-Generic Django Views
**Vulnerability:** Views inheriting directly from base `View` that handle POST requests (such as `AlertMarkReadView`) bypassed `DepartmentFilterMixin` logic and retrieved objects via `get_object_or_404(Alert, pk=pk)` without scoping by user department.
**Learning:** `DepartmentFilterMixin` only works automatically when views override `get_queryset()` or use generic display/editing views. Base `View` handlers with custom `post` methods require manual queryset filtering before calling `get_object_or_404`.
**Prevention:** Always scope querysets by `request.user.department` (or `product__department` for related models) prior to `get_object_or_404` when handling manual view methods for non-admin users.
