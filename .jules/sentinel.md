## 2026-08-25 - IDOR in AlertMarkReadView
**Vulnerability:** Non-admin users ('encargados') could mark alerts from other departments as read by submitting a POST request with an arbitrary alert ID to `AlertMarkReadView`.
**Learning:** `AlertMarkReadView` inherits directly from Django's `View` class and manually retrieves objects via `get_object_or_404(Alert, pk=pk)`, bypassing `DepartmentFilterMixin` or departmental isolation querysets.
**Prevention:** Ensure all custom `View` classes handling single-object operations check user permissions/department isolation when constructing the queryset for `get_object_or_404`.
