## 2026-08-29 - Non-generic View POST methods bypass DepartmentFilterMixin causing IDOR

**Vulnerability:**
The `AlertMarkReadView` handled POST requests via a standard `View.post` method using `get_object_or_404(Alert, pk=pk)` directly. Because `DepartmentFilterMixin` only automatically overrides `get_queryset()` in generic views (like `ListView` or `DetailView`), manual `View` implementations lack automatic department-level scoping, resulting in an Insecure Direct Object Reference (IDOR) vulnerability where users from one department can manipulate resources (marking alerts as read) belonging to another department.

**Learning:**
Generic view mixins like `DepartmentFilterMixin` do not automatically apply isolation rules to custom methods or raw `View` subclasses that do not call `get_queryset()`. Any direct model lookups in manual `post` methods must explicitly inspect the user's role and filter querysets by department/ownership before calling `get_object_or_404`.

**Prevention:**
When using raw `View` subclasses or overriding HTTP handlers manually, explicitly construct a filtered queryset using `request.user.department` (or relevant relationship) for non-admin users prior to fetching objects by primary key.
