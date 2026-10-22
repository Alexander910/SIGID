## 2026-10-22 - Non-Generic View.post Methods Bypass DepartmentFilterMixin
**Vulnerability:** IDOR in `AlertMarkReadView` allowed non-admin users to mark alerts belonging to other departments as read.
**Learning:** Generic class-based views using `DepartmentFilterMixin` apply department restrictions via `get_queryset()`. However, custom `View` subclasses implementing a manual `post()` method bypass `get_queryset()` unless explicit queryset filtering is performed before calling `get_object_or_404()`.
**Prevention:** Always filter querysets explicitly by `request.user.department` (or related model path like `product__department`) when fetching objects in manual `View` handlers.
