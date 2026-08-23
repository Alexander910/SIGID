## 2026-08-23 - Custom View post methods bypass DepartmentFilterMixin
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView` where non-admin users could mark any alert as read by ID.
**Learning:** Generic class-based views using `DepartmentFilterMixin` automatically restrict querysets, but custom views inheriting directly from `View` bypass mixin filtering logic unless explicitly enforced in `get_object_or_404` or queryset filtering.
**Prevention:** Always filter QuerySets by `request.user.department` (or `product__department`) when performing manual object retrieval in custom `View.post` methods for non-admin users.
