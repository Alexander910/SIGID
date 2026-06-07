## 2025-05-15 - IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Non-admin users could mark any alert as read by guessing its ID via a POST request, bypassing department-level isolation.
**Learning:** Views inheriting from the base `View` class and manually calling `get_object_or_404` on the Model class bypass the department-level filtering provided by `DepartmentFilterMixin` (which only overrides `get_queryset`).
**Prevention:** Always filter the queryset by the user's department (e.g., `product__department`) before calling `get_object_or_404` in non-generic views.
