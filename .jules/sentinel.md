## 2025-07-13 - Fix IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) in the `AlertMarkReadView.post` method allowed authenticated users to mark alerts from any department as read by providing the alert's primary key.
**Learning:** Manual `post` implementations in views inheriting from the base `View` class bypass the automatic queryset filtering logic of `DepartmentFilterMixin`. These views require explicit departmental filtering when calling `get_object_or_404`.
**Prevention:** Ensure all manual object lookups in views include departmental or ownership constraints in the queryset passed to `get_object_or_404`.
