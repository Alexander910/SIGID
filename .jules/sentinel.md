## 2025-05-15 - [IDOR in Alert Marking]
**Vulnerability:** IDOR (Insecure Direct Object Reference) in `AlertMarkReadView`.
**Learning:** Generic Django `View` classes that implement manual `post` methods bypass `DepartmentFilterMixin` logic if it is only applied to the queryset of generic views like `ListView`. Direct `get_object_or_404(Model, pk=pk)` calls without explicit filtering by the owner's relation (e.g., department) allow unauthorized actions.
**Prevention:** Always filter the queryset by the user's authorization boundary (e.g., `request.user.department`) before performing actions on a specific object ID in manual view methods. Use `get_object_or_404(filtered_queryset, pk=pk)` instead of the model class directly.
