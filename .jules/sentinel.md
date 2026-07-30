## 2026-05-07 - Insecure Direct Object Reference (IDOR) on Alert Marking
**Vulnerability:** The `AlertMarkReadView` class in `alertas/views.py` allowed non-admin users (encargados) to mark as read alerts belonging to any department by manually providing the alert ID in the URL.
**Learning:** While the application uses `DepartmentFilterMixin` for list views, custom non-generic views that handle single object modifications (like POST actions inheriting directly from `View`) bypass the automatic queryset filtering provided by generic Django views.
**Prevention:** Always explicitly filter querysets by the appropriate relationship (e.g., `product__department`) before performing database lookup using `get_object_or_404` in custom views, especially for non-admin users.
