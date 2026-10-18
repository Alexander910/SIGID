## 2026-10-18 - IDOR in Manual View.post Methods Bypassing Mixins
**Vulnerability:** `AlertMarkReadView` directly fetched `Alert` objects using `get_object_or_404(Alert, pk=pk)` without checking the user's department, enabling cross-department unauthorized state changes (IDOR).
**Learning:** Generic Django views inheriting directly from base `View` and overriding `post` methods do not use `DepartmentFilterMixin` logic automatically.
**Prevention:** Always explicitly filter `get_object_or_404` querysets by department for non-admin users in custom POST handlers.
