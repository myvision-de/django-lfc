# django imports
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.backends.file import SessionStore
from django.core.handlers.wsgi import WSGIRequest
from django.core.urlresolvers import reverse
from django.template.loader import get_template_from_string
from django.template import Context
from django.test import TestCase
from django.test.client import Client

# lfc imports
from lfc.manage.forms import CoreDataForm
from lfc.models import BaseContent
from lfc.models import Page
from lfc.models import Portal

# Taken from "http://www.djangosnippets.org/snippets/963/"
class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function,
    just as if that view had been hooked up using a URLconf.

    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)

def create_request():
    """
    """
    rf = RequestFactory()
    request = rf.get('/')
    request.session = SessionStore()

    user = User()
    user.is_superuser = True
    user.save()
    request.user = user

    return request

class PageTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        self.p = Portal.objects.create()
        self.p1 = Page.objects.create(title="Page 1", slug="page-1")
        self.p11 = Page.objects.create(title="Page 1-1", slug="page-1-1", parent=self.p1)
        self.p111 = Page.objects.create(title="Page 1-1-1", slug="page-1-1-1", parent=self.p11)
        self.p12 = Page.objects.create(title="Page 1-2", slug="page-1-2", parent=self.p1)

    def test_page_defaults(self):
        """Tests the default values of a freshly added page.
        """
        self.assertEqual(self.p1.title, "Page 1")
        self.assertEqual(self.p1.slug, "page-1")
        self.assertEqual(self.p1.display_title, True)
        self.assertEqual(self.p1.position, 1)
        self.assertEqual(self.p1.language, "0")
        self.assertEqual(self.p1.canonical, None)
        self.assertEqual(self.p1.tags, "")
        self.assertEqual(self.p1.parent, None)
        self.assertEqual(self.p1.template, None)
        self.assertEqual(self.p1.standard, None)
        self.assertEqual(self.p1.active, False)
        self.assertEqual(self.p1.exclude_from_navigation, False)
        self.assertEqual(self.p1.exclude_from_search, False)
        self.assertEqual(self.p1.creator, None)
        self.assertEqual(len(self.p1.images.all()), 0)
        self.assertEqual(self.p1.allow_comments, 1)
        self.assertEqual(self.p1.searchable_text, "Page 1")

        self.assertEqual(self.p1.meta_keywords, "<tags>")
        self.assertEqual(self.p1.meta_description, "<description>")

        self.assertEqual(self.p1.content_type, "page")

    def test_get_absolute_url(self):
        """
        """
        self.p1.language = settings.LANGUAGE_CODE
        self.p1.save()

        url = self.p1.get_absolute_url()
        self.assertEqual(url, "/page-1")

        self.p11.language = settings.LANGUAGE_CODE
        self.p11.save()

        url = self.p11.get_absolute_url()
        self.assertEqual(url, "/page-1/page-1-1")

    def test_get_content_object(self):
        """
        """
        bc = BaseContent.objects.get(slug="page-1")
        ct = bc.get_content_object()

        self.assertEqual(ct, self.p1)

    def test_get_searchable_text(self):
        """
        """
        self.assertEqual(self.p1.get_searchable_text(), "Page 1")

    def test_get_form(self):
        """
        """
        form = self.p1.form()
        self.assertEqual(form.__class__, CoreDataForm)

    def test_get_ancestors(self):
        """
        """
        self.assertEqual(self.p1.get_ancestors(), [])
        self.assertEqual(self.p11.get_ancestors(), [self.p1])
        self.assertEqual(self.p111.get_ancestors(), [self.p11, self.p1])
        self.assertEqual(self.p111.get_reverse_ancestors(), [self.p1, self.p11])

    def test_get_image(self):
        """
        """
        self.assertEqual(self.p1.get_image(), None)

    def test_get_meta_keywords(self):
        """
        """
        self.assertEqual(self.p1.get_meta_keywords(), "")

        self.p1.tags = "Dog, Cat"
        self.assertEqual(self.p1.get_meta_keywords(), "Dog, Cat")

        self.p1.meta_keywords = "<title>"
        self.assertEqual(self.p1.get_meta_keywords(), "Page 1")

        self.p1.meta_keywords = "<description>"
        self.p1.description = "Description"
        self.assertEqual(self.p1.get_meta_keywords(), "Description")

        self.p1.meta_keywords = "<tags>, <title>, <description>"
        self.assertEqual(self.p1.get_meta_keywords(), "Dog, Cat, Page 1, Description")

    def test_get_meta_description(self):
        """
        """
        self.p1.description = "Description"
        self.assertEqual(self.p1.get_meta_description(), "Description")

        self.p1.tags = "Dog, Cat"
        self.p1.meta_description = "<tags>"
        self.assertEqual(self.p1.get_meta_description(), "Dog, Cat")

        self.p1.meta_description = "<title>"
        self.assertEqual(self.p1.get_meta_description(), "Page 1")

        self.p1.meta_description = "<tags>, <title>, <description>"
        self.assertEqual(self.p1.get_meta_description(), "Dog, Cat, Page 1, Description")

    def test_get_template(self):
        """
        """
        self.assertEqual(self.p1.get_template().name, "Article")

    def test_get_title(self):
        """
        """
        self.assertEqual(self.p1.get_title(), "Page 1")

        self.p1.display_title = False
        self.assertEqual(self.p1.get_title(), "")

    def test_is_canonical(self):
        """
        """
        self.assertEqual(self.p1.is_canonical(), True)

    def test_get_canonical(self):
        """
        """
        request = create_request()
        self.assertEqual(self.p1.get_canonical(request), self.p1)

    def test_is_translation(self):
        """
        """
        self.assertEqual(self.p1.is_translation(), False)

    def test_has_language(self):
        """
        """
        request = create_request()
        # Returns True if the object is neutral
        self.assertEqual(self.p1.has_language(request, "en-us"), True)
        self.assertEqual(self.p1.has_language(request, "de"), True)

        self.p1.language = "en-us"
        self.assertEqual(self.p1.has_language(request, "en-us"), True)
        self.assertEqual(self.p1.has_language(request, "de"), False)

    def test_get_translation(self):
        """
        """
        request = create_request()
        self.assertEqual(self.p1.get_translation(request, "en-us"), None)

    def test_are_comments_allowed(self):
        """
        """
        self.assertEqual(self.p1.are_comments_allowed(), False)

