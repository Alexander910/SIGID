## 2025-05-14 - [Vulnerability IDOR in AlertMarkReadView]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Generic Django `View` classes that implement manual `post` methods bypass `DepartmentFilterMixin` logic if it's only applied to `get_queryset` (which generic `View` doesn't use by default in `post`).
**Prevention:** Always use `get_object_or_404` with a filtered queryset in manual `post` methods to ensure data isolation.
