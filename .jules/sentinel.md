## 2025-05-15 - IDOR in views with manual POST methods
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Django views that inherit from base `View` and implement manual `post` methods bypass the `get_queryset` filtering logic provided by `DepartmentFilterMixin` when using `get_object_or_404(Model, pk=pk)`.
**Prevention:** Always use a filtered queryset when fetching objects in manual `post` methods, or ensure the mixin's filtering is explicitly applied to the lookup.
