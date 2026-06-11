## 2025-05-15 - IDOR in AlertMarkReadView
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. Non-admin users could mark any alert as read by providing its ID, even if the alert belonged to a product in a different department.
**Learning:** Views inheriting directly from `django.views.View` instead of using `DepartmentFilterMixin` (which is designed for `ListView`/`DetailView`) often miss automated department-level filtering in their `post` methods.
**Prevention:** Always filter the queryset by the user's department (e.g., `product__department=request.user.department`) when performing actions on specific objects in non-generic views.
