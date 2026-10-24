## 2026-10-24 - Base View Inheritance Bypasses Mixin Filtering in Django Views

**Vulnerability:** In `AlertMarkReadView`, calling `get_object_or_404(Alert, pk=pk)` allowed non-admin users to modify alert states across departments (IDOR / authorization bypass).
**Learning:** Generic class-based views that inherit directly from `django.views.View` and implement custom HTTP methods (e.g., `post`) bypass `DepartmentFilterMixin` logic, requiring manual queryset scoping before object lookup.
**Prevention:** Always scope querysets using `request.user.department` (or related model fields like `product__department`) before performing object retrievals in manual view handlers.
