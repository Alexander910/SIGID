## 2025-05-15 - [IDOR in AlertMarkReadView]
**Vulnerability:** Insecure Direct Object Reference (IDOR) allowed users to mark any alert as read by guessing its primary key in a POST request, bypassing department-level data isolation.
**Learning:** Generic Django `View` classes that implement manual `post` methods do not automatically benefit from `DepartmentFilterMixin` logic if it's only designed for querysets in Class-Based Views (CBVs) like `ListView`.
**Prevention:** Always use filtered querysets with `get_object_or_404` in manual view methods. Prefer using the user's department relationship (e.g., `product__department`) to ensure strict isolation.
