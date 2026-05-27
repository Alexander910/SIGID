## 2025-05-15 - IDOR in non-generic Django Views
**Vulnerability:** Authenticated users could access or modify objects belonging to other departments by providing the object's ID in the URL, bypassing intended data isolation.
**Learning:** While `DepartmentFilterMixin` handles isolation for Django's generic views (ListView, UpdateView, etc.), views inheriting directly from `django.views.View` and using `get_object_or_404(Model, pk=pk)` bypass this protection.
**Prevention:** In non-generic views, manually filter the queryset by the user's department (e.g., `Model.objects.filter(department=request.user.department)`) before calling `get_object_or_404`.
