## 2026-05-16 - [IDOR in Alert Management]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Authenticated users could mark any alert as read by bypassing department-level isolation using its ID.
**Learning:** While the app used `DepartmentFilterMixin` for many list views, simple `View` implementations that performed direct lookups using `get_object_or_404(Model, pk=pk)` lacked the same isolation.
**Prevention:** Always use a filtered queryset or the `DepartmentFilterMixin` logic when performing object lookups in detail or action views to ensure multi-tenancy/department isolation is maintained.
