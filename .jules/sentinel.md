## 2026-08-27 - IDOR Vulnerability in Manual View Post Handlers
**Vulnerability:** `AlertMarkReadView` allowed non-admin users to mark alerts from any department as read by submitting requests with arbitrary alert IDs (IDOR).
**Learning:** Standard Django generic views use `DepartmentFilterMixin` to restrict access, but direct `View` subclasses implementing custom `post` methods bypass mixin queryset filtering if `get_object_or_404(Model, pk=pk)` is called directly on the model manager rather than a filtered queryset.
**Prevention:** Always filter querysets explicitly by user department before retrieving single object instances in custom `View.post` methods (`get_object_or_404(qs, pk=pk)`).
