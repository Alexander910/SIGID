## 2026-09-28 - IDOR in Plain Views Bypassing Mixins
**Vulnerability:** `AlertMarkReadView` inherited directly from `django.views.View` and used `get_object_or_404(Alert, pk=pk)` without checking the user's department, allowing any authenticated user to modify alerts belonging to other departments.
**Learning:** Generic class-based views using `DepartmentFilterMixin` apply department filtering to `get_queryset()`, but custom `View` classes implementing manual `post()` methods bypass this mixin unless the queryset is explicitly filtered.
**Prevention:** Always filter the queryset by `request.user.department` (or relational path such as `product__department`) before invoking `get_object_or_404` in non-generic views.
