## 2025-05-15 - [IDOR in non-generic Views]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Views that inherit directly from Django's base `View` and implement manual `post` methods bypass the automatic queryset filtering provided by `DepartmentFilterMixin` (which relies on `get_queryset`).
**Prevention:** Always use `get_object_or_404` with a filtered queryset instead of the model class directly when performing actions on specific objects in manual `post` or `get` methods.
