## 2025-05-22 - IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Authenticated users could mark any alert as read by sending a POST request with an arbitrary alert ID, bypassing department-level isolation.
**Learning:** Views that inherit directly from Django's base `View` class and implement custom `post` methods do not automatically benefit from `DepartmentFilterMixin` or similar queryset-limiting mixins that typically override `get_queryset`.
**Prevention:** Always manually filter querysets in non-generic views (e.g., those using `View.post`) based on the user's permissions or department before performing operations on specific objects.
