## 2026-09-06 - Manual View.post Methods Bypassing Department Isolation Mixins
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView` allowed non-admin users to mark alerts from other departments as read by submitting requests with arbitrary alert IDs.
**Learning:** Base `View` classes implementing manual `post` methods do not automatically utilize `DepartmentFilterMixin` or class-based queryset filtering, making direct `get_object_or_404(Model, pk=pk)` calls vulnerable to IDOR.
**Prevention:** Always filter the queryset by departmental relationships (e.g. `product__department=request.user.department`) for non-admin users when retrieving instances in custom POST views.
