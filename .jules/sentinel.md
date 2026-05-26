## 2025-05-15 - IDOR in Base View classes
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Users could mark any alert in the system as read by providing its primary key in a POST request, bypassing department-level isolation.
**Learning:** While generic views like `ListView` often use `DepartmentFilterMixin` to secure querysets, custom views inheriting directly from `View` (especially those handling POST/PUT/DELETE) frequently skip these protections if not manually implemented.
**Prevention:** Always filter the base queryset by the owner/department before performing a `get_object_or_404` or similar lookup in non-generic views.
