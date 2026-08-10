## 2026-08-10 - Explicit Department Filtering in Custom POST Views
**Vulnerability:** Insecure Direct Object References (IDOR) on AlertMarkReadView where non-admin users could mark alerts from other departments as read.
**Learning:** Django views inheriting from base `View` that implement manual `post` methods (like `AlertMarkReadView` in `alertas/views.py`) bypass `DepartmentFilterMixin` logic and require explicit department-based filtering in `get_object_or_404` to prevent IDOR.
**Prevention:** Always restrict querysets manually for non-admin users in base `View` implementations before calling `get_object_or_404`, filtering by `product__department=request.user.department` (or relevant relationship path) to enforce department isolation.
