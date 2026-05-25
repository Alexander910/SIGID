## 2025-05-22 - IDOR in Manual POST Views
**Vulnerability:** IDOR in `AlertMarkReadView` (and potentially other non-generic views).
**Learning:** While the project uses `DepartmentFilterMixin` for generic `ListView` and `UpdateView`, views that manually implement `post` (inheriting directly from `View`) often bypass these checks and perform direct object lookups with `get_object_or_404(Model, pk=pk)`.
**Prevention:** Always filter the queryset by user department (or relevant relation like `product__department`) before performing a lookup in manual `post` methods.
