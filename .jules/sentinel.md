## 2026-03-30 - IDOR in AlertMarkReadView
**Vulnerability:** Non-admin users were able to mark alerts belonging to other departments as read by submitting a POST request with the target alert's ID (`pk`).
**Learning:** `AlertMarkReadView` extended base `View` instead of generic views that utilize `DepartmentFilterMixin`. Manually written `post()` views using `get_object_or_404(Model, pk=pk)` bypass department isolation mixins unless the queryset is explicitly scoped.
**Prevention:** Always scope querysets by user authorization/department (e.g. `product__department=request.user.department`) before calling `get_object_or_404` in custom view methods.
