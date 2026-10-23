## 2026-10-23 - IDOR Vulnerability in Custom View Post Handlers

**Vulnerability:** The `AlertMarkReadView` class inherited directly from Django's base `View` rather than `DepartmentFilterMixin` or generic views, and used `get_object_or_404(Alert, pk=pk)` without filtering by department. This allowed non-admin users to mark alerts belonging to other departments as read by supplying a different alert `pk` (Insecure Direct Object Reference).

**Learning:** Base `View` classes with manual `post` methods do not automatically benefit from `DepartmentFilterMixin` or standard queryset isolation. Any custom view fetching objects by primary key must explicitly apply departmental filtering (`product__department` for alerts or `department` for products) when the user is not an administrator.

**Prevention:** Always filter model querysets by `request.user.department` (or foreign key relationship path) prior to `get_object_or_404` or `get()` calls in non-generic view methods for multi-tenant / department-isolated systems.
