## 2026-09-04 - Base View Inheritance Bypasses Mixin Filtering
**Vulnerability:** IDOR in `AlertMarkReadView` where non-admin users could mark alerts from other departments as read.
**Learning:** Classes directly inheriting from Django's `View` (instead of `ListView`/`DetailView`/etc.) do not utilize `DepartmentFilterMixin.get_queryset()`. Manual queryset filtering by `product__department` or user department is necessary when querying models inside `post` or `get` handlers.
**Prevention:** Always verify custom `View` classes that retrieve objects via `get_object_or_404` or `objects.get` perform explicit authorization checks/filtering based on `request.user.department`.
