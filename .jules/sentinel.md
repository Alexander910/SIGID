## 2026-10-07 - IDOR in Manual View POST Handlers
**Vulnerability:** `AlertMarkReadView` retrieved `Alert` objects directly by primary key without department restrictions for non-admin users, leading to IDOR.
**Learning:** Generic class-based views with `DepartmentFilterMixin` apply department filtering automatically in `get_queryset`, but custom `View` classes with manual `post()` methods bypass `get_queryset()` and require explicit queryset filtering before calling `get_object_or_404`.
**Prevention:** Always construct a department-filtered queryset before calling `get_object_or_404` in manual view action handlers when operating on department-isolated resources.
