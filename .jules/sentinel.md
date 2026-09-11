## 2026-09-11 - View Subclasses Bypassing Mixin Scoping IDOR
**Vulnerability:** Non-generic Django `View` classes implementing custom HTTP handlers (such as `AlertMarkReadView.post`) bypass mixins like `DepartmentFilterMixin` because they perform direct `get_object_or_404(Model, pk=pk)` calls on unfiltered querysets.
**Learning:** `DepartmentFilterMixin` only modifies `get_queryset()` for generic class-based views (e.g., `ListView`, `UpdateView`). Standard `View` implementations need explicit queryset filtering based on user permissions or department scope prior to `get_object_or_404`.
**Prevention:** Always filter model querysets by user authorization scope (e.g., `product__department=request.user.department`) before calling `get_object_or_404` in non-generic view methods.
