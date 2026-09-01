## 2026-09-01 - Department filter mixin bypass on custom View POST methods

**Vulnerability:** In `alertas/views.py`, `AlertMarkReadView` directly fetched an `Alert` object using `get_object_or_404(Alert, pk=pk)` without enforcing department-level access control. This allowed authenticated non-admin users to mark alerts belonging to other departments as read (IDOR vulnerability).

**Learning:** Base `View` classes with custom `post` methods do not automatically benefit from `DepartmentFilterMixin` logic unless explicitly applied to the queryset inside the view method.

**Prevention:** Always filter model querysets by user department (e.g., `product__department=request.user.department`) before looking up objects in custom endpoints for non-admin users.
