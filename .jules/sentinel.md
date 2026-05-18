## 2025-05-14 - IDOR in Custom View Lookups
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** While `DepartmentFilterMixin` was correctly applied to `ListView`, custom `View` classes performing manual object lookups with `get_object_or_404(Model, pk=pk)` bypassed the department-level isolation logic.
**Prevention:** Always filter the queryset by `department` (for non-admins) before calling `get_object_or_404` or similar lookup methods in custom views.
