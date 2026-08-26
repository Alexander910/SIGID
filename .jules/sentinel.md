## 2026-08-26 - IDOR in View.post Direct Object Lookup
**Vulnerability:** `AlertMarkReadView` allowed non-admin users to mark alerts belonging to other departments as read by submitting requests with arbitrary alert primary keys (`pk`).
**Learning:** Generic `View` sub-classes that implement custom `post` handlers bypass `DepartmentFilterMixin` queryset filtering, leaving `get_object_or_404(Alert, pk=pk)` unconstrained unless explicitly filtered by department (`product__department`).
**Prevention:** Always restrict querysets passed to `get_object_or_404` or object lookups in custom `View` handlers based on user roles and department boundaries.
