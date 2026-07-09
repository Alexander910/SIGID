## 2025-05-15 - [IDOR in Non-Generic Views]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Views inheriting from the base `View` class and implementing manual `post` methods do not automatically benefit from `DepartmentFilterMixin` or similar queryset-based isolation. `get_object_or_404(Model, pk=pk)` is inherently vulnerable if the model is not manually filtered by the user's authorization context (e.g., department).
**Prevention:** Always use a filtered queryset in `get_object_or_404` for non-admin users. Example: `get_object_or_404(Alert.objects.filter(product__department=request.user.department), pk=pk)`.
