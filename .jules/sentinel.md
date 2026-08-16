## 2026-08-16 - Manual View IDOR Bypass of Mixins
**Vulnerability:** IDOR in `AlertMarkReadView` where non-admin users could mark alerts from any department as read by submitting POST requests with any alert ID.
**Learning:** Generic views inheriting directly from base `View` and overriding action methods (like `post`) bypass `DepartmentFilterMixin` query isolation, requiring explicit queryset filtering before calling `get_object_or_404`.
**Prevention:** Always filter the queryset by `request.user.department` or relevant relationship paths (`product__department`) when performing manual lookup operations in custom `View` classes for non-admin users.
