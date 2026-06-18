## 2025-05-15 - AlertMarkReadView IDOR Vulnerability
**Vulnerability:** The `AlertMarkReadView` allowed any authenticated user to mark any alert as read by providing its ID in the POST request, regardless of whether the alert belonged to their department.
**Learning:** Generic `View` classes that implement manual `post` methods (like `AlertMarkReadView`) do not benefit from `DepartmentFilterMixin` because they don't use the standard `get_queryset` or `get_object` methods of generic views like `UpdateView` or `DeleteView`.
**Prevention:** Always manually filter by department (or the appropriate ownership relationship) when using `get_object_or_404` or direct queryset lookups in manual view methods.
