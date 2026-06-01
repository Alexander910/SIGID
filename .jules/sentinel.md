## 2025-05-23 - IDOR in Alertas
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Authenticated users could mark any alert as read by its ID, regardless of their department.
**Learning:** Views inheriting from the base `View` class (rather than generic views like `UpdateView`) often bypass `DepartmentFilterMixin` logic, requiring manual queryset filtering in methods like `post`.
**Prevention:** Always filter querysets by the user's department or relevant relationship before calling `get_object_or_404` in custom views.
