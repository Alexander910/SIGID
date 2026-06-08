## 2025-05-15 - [IDOR in AlertMarkReadView]
**Vulnerability:** Insecure Direct Object Reference (IDOR) allowed users to mark alerts from other departments as read by providing their ID in the POST request.
**Learning:** Views inheriting directly from `django.views.View` (instead of generic views like `UpdateView`) often skip the protections provided by `DepartmentFilterMixin`, which only overrides `get_queryset`. If the view's method (like `post`) performs a direct `get_object_or_404(Model, pk=pk)`, it bypasses any department-level filtering.
**Prevention:** For manual `View` implementations, always filter the queryset by the user's authorized scope (e.g., `request.user.department`) before retrieving objects by ID.
