## 2025-07-24 - IDOR in Base View Class Post Method
**Vulnerability:** Logged-in non-admin users could mark any alert in the system as read via the `AlertMarkReadView` POST endpoint by manipulating the primary key (`pk`), bypassing department-level data isolation.
**Learning:** Generic Django views using `DepartmentFilterMixin` safely filter queries, but direct subclasses of the base `View` that implement manual request handling (such as `post`) bypass mixin methods like `get_queryset` and perform direct, unfiltered queries.
**Prevention:** Always filter the queryset based on the request user's department before executing queries (`get_object_or_404`, `filter`, etc.) inside manual view methods or when `DepartmentFilterMixin` is not automatically applied.
