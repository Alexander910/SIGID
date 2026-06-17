## 2025-05-15 - [IDOR in AlertMarkReadView]
**Vulnerability:** Insecure Direct Object Reference (IDOR) allowed any authenticated user to mark any alert as read, even if the alert belonged to a product in a different department.
**Learning:** Views that inherit directly from Django's base `View` class instead of generic views (like `DetailView` or `UpdateView`) often bypass the filtering logic provided by `DepartmentFilterMixin`, which only overrides `get_queryset`.
**Prevention:** Always manually filter the queryset when using `get_object_or_404` or similar methods in custom `View` methods, or use generic views that correctly utilize `get_queryset`.
