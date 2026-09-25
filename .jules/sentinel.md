## 2026-09-25 - IDOR in Alert Management Views

**Vulnerability:**
In `AlertMarkReadView`, any authenticated user could issue a POST request with the primary key of an alert belonging to any department and mark it as read, bypassing departmental access controls (IDOR).

**Learning:**
Generic views using custom `post` methods without inheriting from or overriding `get_queryset()` or using `DepartmentFilterMixin` do not automatically restrict queries by user department. Manual `get_object_or_404` lookups on `Alert` (or other models) without explicit queryset filtering bypass data isolation rules.

**Prevention:**
Always construct a department-filtered queryset before calling `get_object_or_404` in custom view methods for non-admin users.
