## 2026-08-12 - IDOR in AlertMarkReadView
**Vulnerability:** Non-admin users could mark any alert in the database as read by passing a direct object identifier (ID) because the lookup did not restrict queries by the user's department.
**Learning:** Django views that inherit directly from View and manually implement POST endpoints bypass the query filtering mixins like DepartmentFilterMixin (which only apply to default generic views). This creates high-priority authorization bypass/IDOR risks if manual filtering is omitted.
**Prevention:** Always perform department filtering manually when using get_object_or_404 or filtering the queryset in custom views and actions. Use product__department=request.user.department to ensure strict data isolation.
