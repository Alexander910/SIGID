## 2025-05-15 - IDOR in View-based Post Methods
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Non-admin users could mark any alert as read by providing its ID, even if it belonged to a different department.
**Learning:** Views inheriting from the base `View` class (rather than generic views) bypass the automatic filtering provided by `DepartmentFilterMixin`. Manual filtering of the queryset in the `post` method is required.
**Prevention:** Always filter the queryset by `request.user.department` (or relevant relationship) before using `get_object_or_404` or performing updates in custom `View` classes.
