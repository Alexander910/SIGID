## 2026-08-28 - IDOR Bypass in Hand-Written View Handlers

**Vulnerability:** `AlertMarkReadView` retrieved `Alert` objects directly by `pk` using `get_object_or_404(Alert, pk=pk)` without checking whether non-admin users belonged to the same department as the product associated with the alert.

**Learning:** Views inheriting directly from Django's base `View` and overriding HTTP methods manually (such as `post`) do not automatically inherit `DepartmentFilterMixin` behavior, leading to potential IDOR security gaps if lookup querysets are not explicitly filtered.

**Prevention:** Always filter target model querysets by user authorization scope (e.g. `product__department=request.user.department` for non-admins) prior to calling `get_object_or_404` in custom view methods.
