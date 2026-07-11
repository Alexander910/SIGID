## 2025-05-15 - IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) allowed any authenticated user to mark any alert as read by simply providing the alert ID in the POST request.
**Learning:** Generic Django views often use `DepartmentFilterMixin` for automatic filtering, but manual `View.post` methods bypass this logic. These require explicit filtering in `get_object_or_404`.
**Prevention:** Always verify object ownership or departmental association in non-generic views that perform state-changing operations.
