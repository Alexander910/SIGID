## 2026-06-04 - IDOR in View-based subclasses
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Authenticated users could mark any alert as read by guessing or manipulating the alert ID in the POST request.
**Learning:** Generic class-based views that inherit from `View` (instead of `ListView`, `UpdateView`, etc.) do not automatically use `DepartmentFilterMixin` logic if it's only applied to `get_queryset`. Manual filtering in methods like `post` is necessary.
**Prevention:** Always filter the queryset by the user's department (or relevant authorization attribute) before performing operations on specific objects retrieved via user-supplied IDs.
