## 2025-05-15 - [IDOR in Base View classes]
**Vulnerability:** Insecure Direct Object Reference (IDOR) in `AlertMarkReadView`.
**Learning:** Generic views like `UpdateView` often benefit from mixins that filter querysets, but custom `View` subclasses (using `post` or `get` directly) often perform manual `get_object_or_404(Model, pk=pk)` which bypasses these filters if not carefully implemented.
**Prevention:** Always use a filtered queryset (matching the user's permissions) when fetching objects by ID in custom views.

## 2025-05-15 - [POST Data Tampering for Department isolation]
**Vulnerability:** Authorization bypass via POST data tampering in `ProductUpdateView`.
**Learning:** Hiding fields in the UI (e.g., using `HiddenInput` or excluding from form) provides a good UX but no security. Malicious users can still submit these fields in the POST request.
**Prevention:** Enforce authorization constraints in the `form_valid` method or the service layer, overriding any user-submitted data for restricted fields.
