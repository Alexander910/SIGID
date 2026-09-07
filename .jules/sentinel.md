## 2026-09-07 - Non-generic View post methods bypass DepartmentFilterMixin
**Vulnerability:** IDOR in views directly inheriting from base `View` where POST requests process `pk` without filtering queryset by department.
**Learning:** `DepartmentFilterMixin` only works automatically on generic class-based views that utilize `get_queryset()` (e.g. `ListView`, `UpdateView`). Direct `View` subclasses implementing custom `post` methods bypass mixin filtering if `get_object_or_404(Model, pk=pk)` is used directly.
**Prevention:** Always filter querysets manually with `request.user.department` (or relation like `product__department`) before passing to `get_object_or_404` in non-generic views.
