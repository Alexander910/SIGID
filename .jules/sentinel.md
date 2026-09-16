## 2026-09-16 - Manual POST View Logic IDOR Vulnerability
**Vulnerability:** `AlertMarkReadView` directly fetched `Alert` objects using `get_object_or_404(Alert, pk=pk)` without filtering by department for non-admin users, allowing IDOR cross-department alert modification.
**Learning:** Generic views like `ListView` utilize `DepartmentFilterMixin`, but custom `View` classes with manual `post` methods bypass mixin query filtering unless explicitly filtered.
**Prevention:** Always construct/filter the model queryset using `request.user.department` (or appropriate relationship path) prior to invoking `get_object_or_404` in manual view handlers.
