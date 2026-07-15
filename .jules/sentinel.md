## 2026-07-15 - [IDOR in Manual POST View]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Django views inheriting directly from `View` and implementing manual `post` methods bypass the `DepartmentFilterMixin` logic (which relies on `get_queryset`). Even if the mixin was added, manual calls to `get_object_or_404(Model, pk=pk)` ignore it.
**Prevention:** Always use a filtered queryset in `get_object_or_404` for views that perform actions on specific objects, especially when not using generic class-based views that automatically handle queryset filtering.
