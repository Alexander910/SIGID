## 2025-05-15 - [IDOR in AlertMarkReadView]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. A user could mark any alert as read by providing its ID in a POST request, regardless of whether the alert belonged to their department.
**Learning:** Generic views that implement manual `post` methods (like those inheriting from `View`) do not automatically benefit from `DepartmentFilterMixin` logic if it's only implemented in `get_queryset` (which `View` doesn't use by default in `post`).
**Prevention:** Always filter the queryset by the appropriate ownership/department field when using `get_object_or_404` in manual view methods.
