## 2026-11-04 - IDOR in AlertMarkReadView
**Vulnerability:** AlertMarkReadView permitted non-admin users to mark alerts belonging to other departments as read by submitting a POST request with the alert ID.
**Learning:** Generic View implementations that override `post()` bypass `DepartmentFilterMixin` query restrictions, requiring explicit department filtering before `get_object_or_404`.
**Prevention:** Always verify departmental ownership using `request.user.department` on single-object action views when not using generic detail/edit views.
