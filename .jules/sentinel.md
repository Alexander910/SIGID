## 2026-08-13 - [IDOR in AlertMarkReadView]
**Vulnerability:** The `AlertMarkReadView` allowed any authenticated user to mark any alert as read, regardless of the department associated with the alert's product, leading to Insecure Direct Object Reference (IDOR).
**Learning:** Standard Django Views that implement a custom `post` method manually bypass the automatic department filtering of `DepartmentFilterMixin` if they do not explicitly restrict the lookup queryset or object.
**Prevention:** Always restrict lookups in manual POST/GET methods using `get_object_or_404` filtered by `product__department` or similar fields for non-admin users, or implement explicit permission checking within the method.
