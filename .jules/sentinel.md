## 2026-10-09 - Django Base View POST Methods Bypass Mixin Queryset Filtering
**Vulnerability:** IDOR in `AlertMarkReadView` allowed non-admin users from one department to mark alerts belonging to another department as read by making a POST request with the alert PK.
**Learning:** Generic views inheriting directly from base `View` and defining manual `post()` methods bypass `DepartmentFilterMixin`'s `get_queryset()` logic unless explicitly filtered in `get_object_or_404`.
**Prevention:** Always filter the queryset by user permissions/department before calling `get_object_or_404` in custom `View` classes with manual `post` handling.
