# Sentinel's Journal - Critical Security Learnings

## 2026-08-09 - AlertMarkReadView IDOR Prevention
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView` allowed non-admin users to mark arbitrary alerts as read by simply providing their ID in a POST request, bypassing department-level data isolation.
**Learning:** While the system employs `DepartmentFilterMixin` on generic class-based views for automatic data isolation, custom non-generic views that override the `post` method bypass this mixin's queryset filtering and must manually apply department filters when querying model instances.
**Prevention:** Always verify that custom Django POST handlers perform manual filtering on the model querysets using the logged-in user's department attributes before fetching objects with `get_object_or_404` or similar lookup methods.
