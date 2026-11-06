## 2026-11-06 - Insecure Direct Object Reference (IDOR) in AlertMarkReadView
**Vulnerability:** AlertMarkReadView fetched Alert objects directly by primary key without scoping to the requesting user's department, allowing authenticated users with the 'encargado' role to mark alerts belonging to other departments as read.
**Learning:** Custom View classes implementing manual `post` methods do not automatically benefit from DepartmentFilterMixin or generic view filtering patterns, creating IDOR vulnerabilities if `get_object_or_404` queries the unconstrained model directly.
**Prevention:** Always scope queries in custom POST/action views by user department for non-admin users (e.g., `product__department=request.user.department`) before retrieving target objects.
