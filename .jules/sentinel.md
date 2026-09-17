## 2026-09-17 - Custom View Subclasses Bypass DepartmentFilterMixin Querysets
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView` allowed non-admin users to modify alerts belonging to products in other departments.
**Learning:** `AlertMarkReadView` inherited directly from Django's base `View` rather than generic display/editing views or using `DepartmentFilterMixin`, causing `get_object_or_404(Alert, pk=pk)` to query the entire `Alert` table without tenant/department scoping.
**Prevention:** For custom `View` subclasses or methods performing manual object lookups, always construct a scoped queryset filtering by `product__department` (or relevant relation) for non-admin users before invoking `get_object_or_404`.
