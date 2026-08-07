## 2026-08-07 - [HIGH] Fix IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) on the single alert mark as read endpoint (`/alertas/<int:pk>/leida/`). Non-admin users ('encargados') could mark alerts from any department as read by directly referencing the alert ID in a POST request.
**Learning:** Generic Django Views inheriting from `View` bypass the automatic `DepartmentFilterMixin` query restriction logic, leaving manually implemented `post` methods vulnerable to IDOR unless the querysets are explicitly filtered.
**Prevention:** Always restrict querysets manually using `get_object_or_404` with user-department filtering on endpoints that handle object retrieval or modification in non-generic/raw Django Views.
