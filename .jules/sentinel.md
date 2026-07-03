## 2026-07-03 - IDOR in Manual View Methods
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Authenticated users could mark any alert in the system as read by providing its ID, bypassing departmental isolation.
**Learning:** Generic class-based views using `DepartmentFilterMixin` are protected because they use `get_queryset`. However, manual `View` implementations that directly call `get_object_or_404` on the model manager bypass this protection.
**Prevention:** In manual view methods (`get`, `post`, etc.), always apply departmental filtering to the queryset before fetching an object: `get_object_or_404(Model.objects.filter(department=user.department), pk=pk)`.
