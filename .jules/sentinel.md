## 2026-09-29 - Manual View POST Methods Bypass Mixin Filtering
**Vulnerability:** In `AlertMarkReadView`, `get_object_or_404(Alert, pk=pk)` allowed non-admin users to mark alerts belonging to other departments as read (IDOR).
**Learning:** Base `View` classes that implement manual `post` methods do not use `DepartmentFilterMixin.get_queryset()`, bypassing automated department filtering.
**Prevention:** Always filter the queryset explicitly by `product__department=request.user.department` (or relevant department relationship) for non-admin users prior to calling `get_object_or_404` in manual view handlers.
