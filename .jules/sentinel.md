## 2026-08-20 - Manual POST Views Bypass Department Isolation Mixin
**Vulnerability:** `AlertMarkReadView` allowed non-admin users to mark alerts from any department as read by requesting their primary key directly (IDOR).
**Learning:** Generic class-based views using `DepartmentFilterMixin` apply department filtering to their default querysets, but custom `View` subclasses implementing manual `post` methods (e.g. using `get_object_or_404(Model, pk=pk)`) bypass `DepartmentFilterMixin` logic unless explicitly scoped.
**Prevention:** Always scope querysets manually when using `get_object_or_404` in custom `View` methods for non-admin users: `get_object_or_404(Model.objects.filter(product__department=request.user.department), pk=pk)`.
