## 2026-08-03 - Insecure Direct Object Reference (IDOR) on Alert Marking

**Vulnerability:** The `AlertMarkReadView` endpoint allowed any authenticated user to send a POST request to `/alertas/<pk>/leida/` to mark any arbitrary alert as read, even if the alert belonged to a product under a different department.

**Learning:** Views implementing a custom manual `post()` method instead of inheriting from generic views/mixins that implement `get_queryset()` often bypass department-based permission controls, leading to direct object references where only the database PK was validated but not department ownership.

**Prevention:** Always restrict querysets manually inside custom methods using Django `get_object_or_404()` combined with a pre-filtered queryset (such as checking `product__department`) rather than calling `get_object_or_404()` directly on the full model class.
