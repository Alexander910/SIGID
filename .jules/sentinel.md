## 2026-05-28 - [IDOR in AlertMarkReadView]
**Vulnerability:** IDOR (Insecure Direct Object Reference) allowed authenticated users to mark any alert as read by ID, regardless of department.
**Learning:** Manual IDOR protection is needed in non-generic View classes (e.g., within `post` methods) as they bypass the automatic filtering provided by `DepartmentFilterMixin` which is designed for `get_queryset`.
**Prevention:** Always filter the model queryset by the user's department (or relevant relationship) before calling `get_object_or_404` in custom views.
