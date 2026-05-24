## 2025-05-22 - IDOR in Alert Management
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView` allowed users to mark alerts from any department as read by guessing or providing a valid alert ID.
**Learning:** Views inheriting directly from `View` (rather than generic views like `UpdateView`) do not automatically benefit from `DepartmentFilterMixin` when performing individual object lookups in `post` or `get` methods.
**Prevention:** Always filter the queryset by department-related fields (e.g., `product__department`) before calling `get_object_or_404` in custom view methods.
