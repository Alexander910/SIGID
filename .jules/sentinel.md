## 2026-08-31 - IDOR vulnerability in non-generic View subclasses

**Vulnerability:** `AlertMarkReadView` allowed non-admin users to mark alerts belonging to other departments as read by submitting a POST request with any valid alert ID (Insecure Direct Object Reference).
**Learning:** Generic views utilizing `DepartmentFilterMixin` apply department filtering automatically, but custom `View` subclasses implementing manual `post` methods bypass this mixin unless explicit queryset filtering is performed before calling `get_object_or_404`.
**Prevention:** Always filter the queryset by `request.user.department` (or related model field path like `product__department`) for non-admin users inside manual `post` handling methods before calling `get_object_or_404`.
