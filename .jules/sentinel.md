## 2026-11-07 - IDOR in AlertMarkReadView
**Vulnerability:** AlertMarkReadView retrieved Alert objects by primary key directly from Alert.objects without scoping by the authenticated user's department, allowing users with role 'encargado' to mark alerts belonging to other departments as read.
**Learning:** Generic View classes that implement custom HTTP handlers (like `post()`) bypass `DepartmentFilterMixin` logic, leading to missing data isolation checks if objects are retrieved directly with `get_object_or_404(Model, pk=pk)`.
**Prevention:** For views implementing manual `post()` or non-generic logic, always filter querysets by `product__department` (or the appropriate departmental relation) before retrieving objects.
