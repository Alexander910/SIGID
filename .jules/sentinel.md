## 2026-10-31 - IDOR in AlertMarkReadView
**Vulnerability:** AlertMarkReadView fetched Alert objects by primary key directly using `get_object_or_404(Alert, pk=pk)` without scoping the queryset to the user's department, allowing non-admin users ('encargados') to mark alerts from any department as read.
**Learning:** Generic class-based views inheriting from base `View` and implementing custom `post` methods bypass `DepartmentFilterMixin` query isolation logic, requiring manual department filtering on the queryset prior to retrieval.
**Prevention:** Always scope querysets by `product__department` for non-admin users in endpoints that modify or retrieve Alert objects, and write security test cases verifying departmental isolation.
