## 2025-06-19 - Manual View methods bypass DepartmentFilterMixin
**Vulnerability:** Insecure Direct Object Reference (IDOR) in views that override `post()` or other methods manually instead of using generic view flow.
**Learning:** `DepartmentFilterMixin` only works automatically for views that use `get_queryset()` in their standard flow (like `ListView`, `UpdateView`). Views inheriting from base `View` and implementing `post()` manually bypass this protection.
**Prevention:** Always use the `get_object_or_404()` with a filtered queryset in manual methods, or ensure the view correctly uses `get_queryset()`.
