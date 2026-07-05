## 2026-07-05 - [IDOR in AlertMarkReadView]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`. A logged-in user could mark any alert as read by guessing or brute-forcing the alert ID in the POST request, even if the alert belonged to a product in a different department.
**Learning:** Manual implementations of `View.post` methods that bypass generic view mixins (like `DepartmentFilterMixin`) often forget to re-implement necessary security filters.
**Prevention:** Always filter the queryset by the user's authorization boundaries (e.g., department) before performing operations on specific object IDs. Using `get_object_or_404` with a filtered queryset is a robust pattern.
