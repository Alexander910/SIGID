## 2025-05-23 - [Vulnerability Pattern: IDOR in Manual Views]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** While the application uses `DepartmentFilterMixin` for many generic views, manual `View` implementations (like those handling `POST` requests for specific actions) often lack these protections, allowing users to manipulate objects outside their assigned department by simply knowing or guessing an ID.
**Prevention:** Always filter querysets by the user's department (or relevant ownership/isolation field) when performing lookups in manual `View` methods. Using `get_object_or_404(FilteredQuerySet, pk=pk)` is the recommended pattern.
