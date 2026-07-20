# Sentinel's Journal

## 2026-07-20 - IDOR in Base View Post Methods Bypass Mixin
**Vulnerability:** Django views inheriting from base `View` that implement manual `post` methods (like `AlertMarkReadView` in `alertas/views.py`) bypass `DepartmentFilterMixin` logic. This allows users with a specific department scope to modify or view objects belonging to other departments if they know the object ID (Insecure Direct Object Reference).
**Learning:** `DepartmentFilterMixin` only automatically overrides `get_queryset()` for generic views like `ListView`, `DetailView`, `UpdateView`, etc. If a custom view inherits from `View` and implements a manual request handler method like `post()` without explicitly calling a secure filtered queryset or utilizing the mixin's filtering logic, the database objects can be fetched without scope restriction.
**Prevention:** For views implementing manual methods, manually filter the model queryset using the user's department restrictions before calling `get_object_or_404`. For example:
```python
queryset = Model.objects.all()
if request.user.role != 'admin':
    queryset = queryset.filter(relation__department=request.user.department)
obj = get_object_or_404(queryset, pk=pk)
```
