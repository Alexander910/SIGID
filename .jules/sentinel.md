## 2025-05-15 - [IDOR and Unauthorized Data Modification]
**Vulnerability:** IDOR in `AlertMarkReadView` and unauthorized department modification in `ProductUpdateView`.
**Learning:** `DepartmentFilterMixin` only filters querysets for standard generic views. Custom `View` classes (like `AlertMarkReadView`) and `form_valid` overrides in `UpdateView`/`CreateView` must explicitly enforce department-level isolation to prevent users from accessing or modifying data belonging to other departments via IDOR or tampered POST requests.
**Prevention:** Always filter querysets in custom POST handlers and explicitly set department-restricted fields in `form_valid` using `request.user.department` for non-admin users.
