## 2025-05-14 - IDOR in Manual View Post Methods
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Generic views like `ListView` can easily use `DepartmentFilterMixin`, but manual `View.post` implementations often forget to apply the same filtering logic, relying on `get_object_or_404` with the full model manager.
**Prevention:** Always filter the queryset by ownership or department BEFORE calling `get_object_or_404` in manual view methods.
