## 2026-10-16 - Manual HTTP Verb Views Bypass Mixin Isolation
**Vulnerability:** IDOR in `AlertMarkReadView` allowed non-admin users to mark alerts belonging to other departments as read by submitting an arbitrary alert ID in a POST request.
**Learning:** `AlertMarkReadView` inherits directly from `django.views.View` and overrides `post`, which bypasses `DepartmentFilterMixin`'s `get_queryset` filtering mechanism.
**Prevention:** In custom `View` classes handling single object actions, explicitly filter querysets by `request.user.department` (or target relation path like `product__department`) before invoking `get_object_or_404`.
