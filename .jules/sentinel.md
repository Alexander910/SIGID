## 2026-10-19 - Manual View IDOR Bypass on Department Isolation
**Vulnerability:** IDOR in `AlertMarkReadView` allowed non-admin users to modify alert read status for products belonging to other departments.
**Learning:** Base `View` subclasses implementing custom `post` methods bypass `DepartmentFilterMixin` logic because they don't use standard generic view querysets or methods like `get_queryset`.
**Prevention:** Always explicitly filter model querysets by `request.user.department` (or appropriate relationship like `product__department`) before calling `get_object_or_404` in non-generic views.
