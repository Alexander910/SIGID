## 2026-10-04 - Manual View Methods Bypass Department Isolation Mixins
**Vulnerability:** `AlertMarkReadView` allowed any authenticated user to mark alerts belonging to other departments as read via IDOR by supplying any valid alert `pk`.
**Learning:** Generic views relying on custom `View` base classes rather than standard Django generic views (`DetailView`, `UpdateView`) or `DepartmentFilterMixin` bypass automatic queryset scoping.
**Prevention:** Always explicitly filter model querysets by `request.user.department` (or relevant relation like `product__department`) in manual `View` POST handlers before calling `get_object_or_404`.
