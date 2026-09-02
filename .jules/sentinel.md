## 2026-09-02 - Direct View POST Methods Bypass DepartmentFilterMixin IDOR Safeguards

**Vulnerability:** Views inheriting directly from Django's base `View` class (such as `AlertMarkReadView`) fetched model instances using `get_object_or_404(Model, pk=pk)` without checking whether the object belonged to the authenticated non-admin user's department, resulting in an Insecure Direct Object Reference (IDOR).

**Learning:** `DepartmentFilterMixin` only automatically overrides `get_queryset()` for generic class-based views (like `ListView`, `DetailView`, `UpdateView`). Views inheriting from standard `View` that implement custom `post` or `get` logic bypass `DepartmentFilterMixin` entirely unless explicit filtering is applied.

**Prevention:** When implementing endpoints using `View` or custom HTTP methods, explicitly filter the model QuerySet by `request.user.department` (or related paths like `product__department`) for non-admin users before calling `get_object_or_404`.
