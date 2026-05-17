## 2025-05-15 - IDOR in Alert Marking
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Using `get_object_or_404(Model, pk=pk)` without filtering the queryset by the user's scope (e.g., department) allows unauthorized access via direct ID manipulation.
**Prevention:** Always use a filtered queryset or check object-level permissions when fetching objects by ID in views.
