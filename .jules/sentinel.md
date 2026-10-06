## 2026-10-06 - Manual View POST Handlers Bypass Mixin Department Scoping
**Vulnerability:** Non-generic `View` subclasses like `AlertMarkReadView` accepting primary keys in POST requests could mutate objects across department boundaries (IDOR).
**Learning:** `DepartmentFilterMixin` only modifies `get_queryset()` for generic class-based views. Custom views implementing `post()` manually using `get_object_or_404(Model, pk=pk)` do not inherit this filtering automatically.
**Prevention:** Always pass a department-filtered queryset (e.g. `qs.filter(product__department=user.department)`) to `get_object_or_404()` in non-generic views for non-admin users.
