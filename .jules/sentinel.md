## 2026-09-12 - IDOR Bypass in Custom Django View Handlers

**Vulnerability:**
`AlertMarkReadView` handled `POST` requests directly via a custom `View.post` method using `get_object_or_404(Alert, pk=pk)` without filtering by department for non-admin users, allowing cross-department alert modification (IDOR).

**Learning:**
Custom Django `View` classes that do not inherit from generic views or mixins like `DepartmentFilterMixin` bypass automated multi-tenant filtering.

**Prevention:**
Always filter the model queryset explicitly by `request.user.department` (or relevant owner relationship) before invoking `get_object_or_404` in non-generic view handlers.
