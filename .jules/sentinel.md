## 2026-09-19 - IDOR Prevention in Non-Generic Views

**Vulnerability:** IDOR in `AlertMarkReadView` where any logged-in user could mark any alert as read by sending a POST request with its primary key (`pk`).
**Learning:** `AlertMarkReadView` inherits directly from Django's base `View` and manually handles `post`, bypassing `DepartmentFilterMixin` which is designed for generic views.
**Prevention:** Always filter target model querysets by department (`product__department` for alerts) before passing to `get_object_or_404` in custom view methods.
