## 2026-09-27 - Manual View POST Handlers Bypass Department Filter Mixin

**Vulnerability:** IDOR in `AlertMarkReadView` allowed non-admin users to mark alerts belonging to other departments as read.
**Learning:** Views inheriting directly from Django `View` with custom `post` methods do not automatically utilize `DepartmentFilterMixin` querysets unless explicitly queried.
**Prevention:** Always filter model querysets by `request.user.department` (or relevant relation, e.g., `product__department`) when fetching objects in non-generic views for non-admin users.
