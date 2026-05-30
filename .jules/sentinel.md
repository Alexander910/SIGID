## 2025-05-15 - Insecure Direct Object Reference (IDOR) in Base View Methods
**Vulnerability:** Views inheriting directly from Django's base `View` class (like `AlertMarkReadView`) bypassed department-level isolation logic, allowing users to modify objects belonging to other departments by guessing their ID.
**Learning:** Generic mixins like `DepartmentFilterMixin` often only hook into `get_queryset()`, which is automatically used by generic views (ListView, UpdateView) but not by custom `post()` methods in base `View` classes unless explicitly called.
**Prevention:** Always filter the queryset by the user's department (or relevant ownership field) manually within `post()` methods before calling `get_object_or_404()`.

## 2025-05-15 - Trusting Hidden Form Fields for Authorization
**Vulnerability:** `ProductUpdateView` relied on the frontend to "hide" the department field from non-admin users. This allowed malicious users to change a product's department by injecting a different `department` ID into the POST request.
**Learning:** Using `forms.HiddenInput()` or excluding a field from a form only affects the UI; it does not prevent the model's `save()` method from accepting tampered data if the view doesn't explicitly override it.
**Prevention:** In `form_valid()`, always manually set sensitive ownership or categorization fields (like `department`) based on the authenticated user's session data rather than trusting the POST data, especially for UpdateViews.
