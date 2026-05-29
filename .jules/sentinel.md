## 2026-05-29 - IDOR in View-based Post Methods
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Non-admin users could mark any alert as read by sending a POST request with the alert's ID, even if it belonged to another department.
**Learning:** While `DepartmentFilterMixin` handles `get_queryset` for generic views, custom views inheriting directly from `View` (like those handling specific POST actions) often bypass this logic if not manually implemented in the action method (e.g., `post`).
**Prevention:** Always manually filter the queryset by the user's authorized scope (e.g., department) before using `get_object_or_404` in custom view methods.
