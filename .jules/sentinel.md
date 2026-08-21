## 2026-08-21 - IDOR in Manual View POST Handlers

**Vulnerability:** Direct `get_object_or_404(Model, pk=pk)` call in `AlertMarkReadView` allowed non-admin users to mark alerts from other departments as read by specifying the alert ID in POST requests.
**Learning:** Custom views extending base `View` instead of generic `DepartmentFilterMixin` views bypass automatic queryset filtering and require explicit department checks when looking up objects by ID.
**Prevention:** Always filter the queryset by `product__department` or user department before retrieving single model instances using `get_object_or_404` in `post()` or detail view methods.
