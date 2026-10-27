## 2026-10-27 - Manual Views Bypassing Mixin Department Filters

**Vulnerability:** IDOR vulnerability in `AlertMarkReadView` where non-admin users could mark any alert as read regardless of department assignment.
**Learning:** `DepartmentFilterMixin` is designed to filter querysets for generic views (e.g. `ListView`), but standalone `View` classes implementing manual `post` handling and calling `get_object_or_404(Alert, pk=pk)` directly bypass mixin logic unless explicitly filtered.
**Prevention:** Always inspect non-generic `View` subclasses that retrieve objects by primary key and ensure the queryset is explicitly filtered by the requesting user's department before object lookup.
