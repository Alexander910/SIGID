## 2025-05-15 - IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Non-admin users could mark any alert as read by providing its ID in the POST request, bypassing department-level isolation.
**Learning:** Generic `View` implementations that manually handle `post` requests often bypass the `DepartmentFilterMixin` logic, which is typically designed for `ListView` or `DetailView` querysets.
**Prevention:** Always use `get_object_or_404` with a filtered queryset that includes department-level checks for non-admin users in manual view methods.
