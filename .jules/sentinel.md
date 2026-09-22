## 2026-09-22 - IDOR Vulnerability in Custom Django Views
**Vulnerability:** `AlertMarkReadView` in `alertas/views.py` used `get_object_or_404(Alert, pk=pk)` without scoping the queryset to the user's department for non-admin users, leading to Insecure Direct Object Reference (IDOR).
**Learning:** Generic class-based views or base `View` classes that handle manual POST actions bypass `DepartmentFilterMixin` unless querysets are explicitly filtered within the HTTP method handler (e.g. `post`).
**Prevention:** Always filter querysets by `request.user.department` (or appropriate relation path such as `product__department`) before performing object retrieval with `get_object_or_404` in custom view methods.
