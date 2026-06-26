## 2025-05-22 - [HIGH] IDOR in manual View.post methods
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Non-admin users could mark any alert as read by sending a POST request with the alert's ID, even if it belonged to another department.
**Learning:** Django views that inherit from `View` and implement manual `post` methods bypass the automated queryset filtering provided by `DepartmentFilterMixin`. This creates a security gap where object retrieval via `get_object_or_404` doesn't enforce department isolation.
**Prevention:** Always include department-based filtering when using `get_object_or_404` or `get_object` in custom views. For `Alert` models, the filter path is `product__department`.
