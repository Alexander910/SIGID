## 2025-05-15 - IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Any authenticated user can mark any alert as read by providing its ID, even if the alert belongs to a different department.
**Learning:** Generic `View` classes often lack automatic filtering provided by custom mixins like `DepartmentFilterMixin` if not manually implemented in the `post` method.
**Prevention:** Always filter querysets by the user's department (or relevant ownership criteria) when performing actions on specific objects in non-generic views.
