## 2025-05-22 - IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) allowed any authenticated user to mark any alert as read by its ID, regardless of department restrictions.
**Learning:** Generic Django `View` classes that implement manual `post` methods do not automatically benefit from the filtering logic in `DepartmentFilterMixin`, which is designed for generic views like `ListView`.
**Prevention:** Always use filtered querysets with `get_object_or_404` in manual view methods to ensure authorization boundaries are respected.
