## 2026-06-10 - [IDOR in AlertMarkReadView]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Users could mark any alert as read by sending a POST request with the alert's ID, even if the alert belonged to a different department.
**Learning:** Generic Django `View` classes that don't use `DepartmentFilterMixin` (or where the mixin isn't applicable because it's not a generic view with `get_queryset`) require manual filtering in their methods (like `post`) to ensure data isolation.
**Prevention:** Always filter querysets manually when using basic `View` or `APIView` classes for operations on specific objects, especially when role-based data isolation is required.
