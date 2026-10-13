## 2026-10-13 - IDOR Vulnerability in Manual POST Views
**Vulnerability:** `AlertMarkReadView` used `get_object_or_404(Alert, pk=pk)` directly without filtering by department, allowing non-admin users to mark alerts belonging to other departments as read by manipulating the URL `pk`.
**Learning:** `DepartmentFilterMixin` only automatically scopes `get_queryset()` in generic views like `ListView` or `DetailView`. Standard `View` subclasses implementing custom `post()` methods bypass mixin queryset filtering if `get_object_or_404` is invoked directly on model managers.
**Prevention:** Always filter querysets explicitly by `product__department` (or relevant department reference) using `request.user.department` for non-admin users before retrieving objects in manual views.
