## 2025-07-25 - [IDOR in Manual POST View]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Generic views using `DepartmentFilterMixin` are secure by default, but manual `View` implementations with custom `post` methods that use `get_object_or_404(Model, pk=pk)` bypass the mixin's automatic filtering, exposing data across departments.
**Prevention:** Always use a filtered queryset or the `DepartmentFilterMixin` logic within manual `post` methods when retrieving objects by ID.
