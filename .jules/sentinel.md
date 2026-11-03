## 2026-11-03 - IDOR Prevention in Alert Mark Read View
**Vulnerability:** Non-admin users ('encargados') could mark alerts belonging to other departments as read by submitting a POST request with any arbitrary alert ID (`AlertMarkReadView`), bypassing departmental data isolation.
**Learning:** Generic class-based views or base `View` implementations that manually define `post` methods do not automatically utilize `DepartmentFilterMixin` logic, leading to IDOR if `get_object_or_404` directly queries `Alert` without department filtering.
**Prevention:** Always restrict querysets passed to `get_object_or_404` based on the user's role and departmental scope (`product__department`), mirroring the filtering logic in `AlertMarkAllReadView`.
