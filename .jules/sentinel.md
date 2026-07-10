## 2026-07-10 - [IDOR in View.post methods]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in views inheriting from `View` that implement a manual `post` method.
**Learning:** Generic mixins like `DepartmentFilterMixin` typically override `get_queryset`. However, if a view uses `get_object_or_404(Model, pk=pk)` directly in a `post` method without using the view's `get_queryset()` or manually filtering the queryset, it bypasses departmental isolation logic.
**Prevention:** Always use a filtered queryset or call `self.get_queryset()` when retrieving objects in any view method. For non-generic views, explicitly filter by the user's department (or relevant relationship) before fetching the object.
