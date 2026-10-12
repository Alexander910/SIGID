# Sentinel Security Journal

## 2026-10-12 - Non-generic View classes bypass DepartmentFilterMixin
**Vulnerability:** IDOR in `AlertMarkReadView` allowed non-admin users to mark alerts from any department as read by sending a POST request with an arbitrary alert ID (`pk`).
**Learning:** `DepartmentFilterMixin` only automatically hooks into generic class-based views (e.g., `ListView`, `DetailView`, `UpdateView`). Views inheriting directly from `django.views.View` with custom HTTP method implementations (like `post`) bypass `get_queryset()` filtering unless explicitly applied to `Alert.objects` before calling `get_object_or_404`.
**Prevention:** Always verify department ownership when retrieving objects in custom `View.post` or `View.get` methods using explicit queryset filtering (e.g., `qs.filter(product__department=request.user.department)`).
