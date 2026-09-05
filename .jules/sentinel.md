## 2026-09-05 - IDOR in Non-Generic Views Bypassing Mixins

**Vulnerability:**
`AlertMarkReadView` directly fetched an `Alert` object using `get_object_or_404(Alert, pk=pk)` without checking if the associated product's department matched the logged-in user's department, allowing cross-department alert status manipulation (IDOR).

**Learning:**
Views inheriting directly from Django's base `View` rather than `DepartmentFilterMixin`-compatible generic views do not automatically inherit department-level scoping logic.

**Prevention:**
Always construct a filtered queryset based on `request.user.department` (or `product__department`) before calling `get_object_or_404` in custom `View.post` methods.
