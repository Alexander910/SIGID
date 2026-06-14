## 2026-06-14 - [IDOR in View classes]
**Vulnerability:** IDOR (Insecure Direct Object Reference) in `AlertMarkReadView`.
**Learning:** Generic `View` classes that handle POST requests manually often bypass the automatic filtering provided by `DepartmentFilterMixin` (which only affects `get_queryset` typically used in generic views like `ListView`).
**Prevention:** Always manually filter querysets in `View.post` methods or similar manually handled endpoints to ensure object-level authorization is enforced.
