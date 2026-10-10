## 2026-10-10 - Custom POST Views Bypassing Mixin Department Isolation

**Vulnerability:** IDOR in `AlertMarkReadView` where `get_object_or_404(Alert, pk=pk)` allowed non-admin users to modify alerts belonging to other departments.
**Learning:** Generic view mixins (like `DepartmentFilterMixin`) override `get_queryset()` for generic class-based views, but direct base `View` subclasses implementing custom `post` methods bypass `get_queryset()` when calling `get_object_or_404(Model, pk=pk)`.
**Prevention:** Always filter querysets explicitly by department or relation path (`product__department`) before object retrieval in manual `View` POST handlers.
