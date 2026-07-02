## 2026-07-02 - Manual IDOR protection in View.post methods
**Vulnerability:** IDOR (Insecure Direct Object Reference) in `AlertMarkReadView`. Non-admin users could mark any alert as read by guessing or knowing its ID, even if it belonged to a product in a different department.
**Learning:** Generic views like `ListView` that use `DepartmentFilterMixin` are automatically secured, but manual `View.post` (or `get`) implementations that use `get_object_or_404` directly on the model class bypass these protections.
**Prevention:** Always filter the queryset by the user's department (or relevant ownership/isolation criteria) before calling `get_object_or_404` or `objects.get` in custom view methods.
