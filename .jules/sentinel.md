## 2026-08-18 - IDOR via Manual POST Handlers Bypassing Department Filter Mixins
**Vulnerability:** `AlertMarkReadView` directly fetched `Alert` objects using `get_object_or_404(Alert, pk=pk)` without department checks, allowing non-admin users to manipulate alerts belonging to other departments.
**Learning:** Generic class-based views in this codebase inherit `DepartmentFilterMixin` to filter `get_queryset()`, but custom views inheriting directly from `django.views.View` with manual `post` methods bypass `DepartmentFilterMixin` logic unless explicitly filtered.
**Prevention:** Always filter model querysets by department (`product__department` or `department`) in `View` endpoint methods before calling `get_object_or_404` for non-admin users.
