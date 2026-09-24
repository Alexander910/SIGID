## 2026-09-24 - IDOR in Manual POST Views Bypassing Mixin Filtering
**Vulnerability:** In `AlertMarkReadView`, calling `get_object_or_404(Alert, pk=pk)` allowed non-admin users to mark alerts belonging to other departments as read by passing arbitrary primary keys.
**Learning:** Custom views inheriting from base `View` that define manual `post` methods do not automatically use `DepartmentFilterMixin` or `get_queryset()`, resulting in unisolated direct object lookup (`get_object_or_404`).
**Prevention:** Always filter the model queryset explicitly by user authorization attributes (e.g. `request.user.department`) before calling `get_object_or_404` in manual view action handlers.
