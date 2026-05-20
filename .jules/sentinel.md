## 2025-05-14 - IDOR in AlertMarkReadView
**Vulnerability:** An Insecure Direct Object Reference (IDOR) allowed non-admin users to mark alerts from any department as read by submitting their IDs to the `AlertMarkReadView`.
**Learning:** Generic views often use `DepartmentFilterMixin` for automatic filtering, but manual `View` implementations (like `post` methods) bypass this logic, requiring manual queryset filtering to maintain data isolation.
**Prevention:** In manual `post` methods, always filter the queryset used in `get_object_or_404` by the user's department or ownership attributes.
