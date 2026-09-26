## 2026-09-26 - IDOR in Base View HTTP Method Implementations
**Vulnerability:** Views directly inheriting from Django's generic `View` and overriding `post()` without using `DepartmentFilterMixin` or explicit queryset filtering allowed non-admin users to mutate objects (e.g. mark alerts as read) across department boundaries.
**Learning:** `DepartmentFilterMixin` only overrides `get_queryset()`, which standard generic views (e.g. `ListView`, `UpdateView`) utilize, but non-generic `View` subclasses implementing custom handlers like `post()` do not automatically use `get_queryset()` unless explicitly wired.
**Prevention:** In custom `View` methods like `post()`, always construct a department-filtered queryset before calling `get_object_or_404(qs, pk=pk)` for non-admin users.
