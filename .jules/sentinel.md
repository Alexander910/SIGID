## 2024-08-11 - IDOR in Django Custom View POST Methods
**Vulnerability:** Unchecked ID lookup in non-generic custom View POST methods leading to Broken Object Level Authorization (IDOR) on database mutation operations.
**Learning:** While class-based generic views (like `UpdateView` or `DeleteView`) automatically benefit from `DepartmentFilterMixin` by overriding `get_queryset()`, custom views inheriting directly from base `View` and manual POST logic bypass this protection and require explicit database query filtering before object mutation.
**Prevention:** In non-generic views performing direct ID lookups, always apply the user's isolation criteria (e.g., department, owner, account ID) directly to the queryset passed to `get_object_or_404` or the query filters.
