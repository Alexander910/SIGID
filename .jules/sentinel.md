## 2026-07-16 - IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Non-admin users could mark any alert as read by sending a POST request with the alert's ID, even if the alert belonged to a product in a different department.
**Learning:** Generic Django views using `View` and manual `post` methods bypass the automatic filtering provided by `DepartmentFilterMixin` (which only affects `get_queryset` used by generic views like `ListView`, `DetailView`, etc.).
**Prevention:** Always use `get_object_or_404` with a filtered queryset instead of the model class directly when implementing manual POST handlers in views that require data isolation.
