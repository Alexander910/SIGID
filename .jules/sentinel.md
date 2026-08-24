## 2026-08-24 - IDOR Vulnerability in Custom View.post Methods
**Vulnerability:** `AlertMarkReadView` allowed non-admin users to mark alerts belonging to other departments as read by submitting a POST request with any alert primary key ID.
**Learning:** Custom Django `View` classes that implement manual `post` methods do not automatically benefit from `DepartmentFilterMixin` or standard queryset filtering, leading to IDOR risks if `get_object_or_404` is called directly on `Model.objects.all()`.
**Prevention:** Always explicitly filter querysets by tenant/department constraints before retrieving objects in custom `View.post` implementations or use scoped mixins.
