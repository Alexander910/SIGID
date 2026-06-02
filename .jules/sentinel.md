## 2025-05-15 - [IDOR in AlertMarkReadView]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Authenticated users could mark any alert as read regardless of department by providing its primary key in a POST request.
**Learning:** Generic Django `View` classes that manually fetch objects using `get_object_or_404(Model, pk=pk)` bypass department-level isolation logic often implemented in `get_queryset()` of other views (like `ListView` or `UpdateView` with `DepartmentFilterMixin`).
**Prevention:** Always filter the queryset by the appropriate authorization boundary (e.g., `request.user.department`) before retrieving an object by its ID in custom `View` methods.
