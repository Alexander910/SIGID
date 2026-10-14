## 2026-10-14 - IDOR in Manual View Post Methods
**Vulnerability:** In `AlertMarkReadView`, calling `get_object_or_404(Alert, pk=pk)` allowed non-admin users to mark alerts from any department as read.
**Learning:** Generic views inheriting directly from base `View` and implementing a manual `post` method bypass `DepartmentFilterMixin` logic, leading to missing object-level access controls.
**Prevention:** Always filter querysets explicitly by `request.user.department` (or appropriate relational path like `product__department`) when fetching single objects in custom `View` handlers for non-admin users.
