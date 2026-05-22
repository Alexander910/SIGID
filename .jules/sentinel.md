## 2024-05-22 - [IDOR in Base View Methods]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Generic views like `ListView` or `UpdateView` that use `DepartmentFilterMixin` are protected at the queryset level. However, views inheriting from the base `View` class (like `AlertMarkReadView`) that implement custom `post` methods often bypass this protection if they use `get_object_or_404(Model, pk=pk)` directly.
**Prevention:** Always filter the queryset by the user's authorized scope (e.g., department) before passing it to `get_object_or_404` or similar lookup functions in custom view methods.
