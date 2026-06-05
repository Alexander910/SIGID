## 2025-05-15 - IDOR in Alert Management
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Authenticated users could mark any alert as read by its PK, bypassing department-level isolation.
**Learning:** Views inheriting from the base `View` class (rather than generic views with `get_queryset`) often miss automated filtering logic from mixins like `DepartmentFilterMixin` if they don't explicitly use them or manually filter.
**Prevention:** Always filter querysets by the relevant authorization boundary (e.g., `user.department`) when fetching objects by ID in custom views. Use `get_object_or_404` with a filtered queryset.
