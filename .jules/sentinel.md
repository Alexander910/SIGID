## 2025-05-15 - IDOR in manual View.post methods
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Any authenticated user could mark any alert as read by providing its ID, bypassing department isolation.
**Learning:** Generic views like `ListView` or `UpdateView` that use `DepartmentFilterMixin` are protected because they rely on `get_queryset()`. However, manual `View` implementations with a `post` method often use `get_object_or_404(Model, pk=pk)`, which queries the entire table and ignores the mixin's filtering logic.
**Prevention:** Always use a filtered queryset when retrieving objects by ID in manual `post` or `get` methods. For example: `get_object_or_404(Alert.objects.filter(product__department=request.user.department), pk=pk)`.
