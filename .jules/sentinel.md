## 2026-07-26 - IDOR in AlertMarkReadView

**Vulnerability:** Insecure Direct Object Reference (IDOR) on marking alerts as read. The AlertMarkReadView did not filter the Alert queryset by the user's department, allowing any authenticated non-admin user to mark any alert as read by sending its ID.

**Learning:** Base django View sub-classes implementing a manual post method (instead of using standard DetailView or UpdateView with DepartmentFilterMixin) bypass the queryset restriction checks. This creates a risk of IDOR unless the query is explicitly filtered before object retrieval.

**Prevention:** Always filter the queryset on manual view lookups using the user's department (e.g. `Alert.objects.filter(product__department=request.user.department)`). Add comprehensive unit tests verifying that accessing another department's resources returns a 404 response.
