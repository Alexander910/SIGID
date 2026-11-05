## 2026-11-05 - IDOR in AlertMarkReadView
**Vulnerability:** AlertMarkReadView fetched Alert objects by primary key without scoping by the requesting user's department for non-admin users, allowing department managers ('encargado') to mark alerts belonging to other departments as read.
**Learning:** Generic Django views inheriting from base `View` that implement manual `post` methods bypass `DepartmentFilterMixin` logic and require explicit department-based filtering in `get_object_or_404`.
**Prevention:** Always scope querysets by `product__department` or relevant departmental relationships before calling `get_object_or_404` in custom action views.
