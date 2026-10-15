## 2026-10-15 - AlertMarkReadView IDOR Vulnerability
**Vulnerability:** `AlertMarkReadView` retrieved alerts directly by PK via `get_object_or_404(Alert, pk=pk)` without checking department permission, allowing non-admin users to mark alerts from other departments as read (IDOR).
**Learning:** Generic views with `DepartmentFilterMixin` apply department filtering in `get_queryset()`, but custom `View` subclasses implementing manual `post` methods bypass mixin queryset filtering unless explicitly filtered before `get_object_or_404`.
**Prevention:** Always filter model querysets by `request.user.department` (or relevant relationship like `product__department`) when fetching single objects in custom `View.post` methods for non-admin users.
