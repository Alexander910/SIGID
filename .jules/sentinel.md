## 2026-10-28 - IDOR in Manual View.post Methods
**Vulnerability:** `AlertMarkReadView` retrieved `Alert` objects by `pk` without filtering by user department, allowing non-admin users to mark alerts from other departments as read.
**Learning:** Generic class-based views inheriting from base `View` that implement manual `post()` methods bypass class mixins like `DepartmentFilterMixin` unless querysets are explicitly filtered.
**Prevention:** Always filter model querysets using `request.user.department` (or relevant relation) before calling `get_object_or_404()` in custom `View` POST handlers.
