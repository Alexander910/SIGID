from django.test import TestCase
from django.conf import settings


class SecurityHeadersTest(TestCase):
    """Test suite to verify security settings and response headers."""

    def test_security_settings_configured(self):
        """Verify that essential security settings are properly set in Django settings."""
        self.assertTrue(getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False))
        self.assertTrue(getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False))
        self.assertEqual(getattr(settings, 'X_FRAME_OPTIONS', None), 'DENY')
        self.assertTrue(getattr(settings, 'SESSION_COOKIE_HTTPONLY', False))
        self.assertTrue(getattr(settings, 'CSRF_COOKIE_HTTPONLY', False))

    def test_security_headers_in_response(self):
        """Verify that HTTP responses contain expected security headers."""
        response = self.client.get('/login/')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
