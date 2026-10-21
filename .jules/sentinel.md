## 2026-10-21 - IDOR in View.post method bypassing mixin filtering
**Vulnerability:** Non-admin users were able to mark alerts as read for products belonging to other departments by POSTing directly to `/alertas/<pk>/read/`.
**Learning:** Custom `View` subclasses implementing `post` methods (like `AlertMarkReadView`) do not automatically inherit `DepartmentFilterMixin` behavior unless explicitly applied to a queryset prior to calling `get_object_or_404`.
**Prevention:** Always filter querysets explicitly by `request.user.department` (or relevant relationship like `product__department`) inside custom endpoint handlers before fetching objects using `get_object_or_404`.
