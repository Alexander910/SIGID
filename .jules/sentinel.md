## 2025-05-14 - IDOR in Alert marking
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Users could mark any alert as read by knowing its ID, regardless of their department.
**Learning:** Generic Django `View` classes that implement manual `post` methods bypass the `DepartmentFilterMixin` logic if not explicitly handled, as they often use `get_object_or_404` on the full model manager.
**Prevention:** Always filter the queryset by user department before performing lookups in manual POST/PUT methods, even when using mixins that affect `get_queryset`.
