from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils.importlib import import_module

from celery import Celery
from reviewboard.extensions.base import Extension

from reviewbotext.handlers import SignalHandlers
from reviewbotext.models import ReviewBotTool
from reviewbotext.resources import review_bot_review_resource, \
                                   review_bot_tool_resource


class ReviewBotExtension(Extension):
    """An extension for communicating with Review Bot"""
    is_configurable = True
    has_admin_site = True
    default_settings = {
        'ship_it': False,
        'comment_unmodified': False,
        'open_issues': False,
        'BROKER_URL': '',
        'rb_url': '',
        'user': None,
    }
    resources = [
        review_bot_review_resource,
        review_bot_tool_resource,
    ]

    def __init__(self, *args, **kwargs):
        super(ReviewBotExtension, self).__init__()
        self.settings.load()
        self.celery = Celery('reviewbot.tasks')
        self.signal_handlers = SignalHandlers(self)

    def shutdown(self):
        self.signal_handlers.disconnect()
        super(ReviewBotExtension, self).shutdown()

    def notify(self, request_payload):
        """Add the request to the queue."""
        self.celery.conf.BROKER_URL = self.settings['BROKER_URL']

        review_settings = {
            'ship_it': self.settings['ship_it'],
            'comment_unmodified': self.settings['comment_unmodified'],
            'open_issues': self.settings['open_issues'],
        }
        payload = {
            'url': self.settings['rb_url'],
            'ship_it': self.settings['ship_it'],
            'request': request_payload,
            'settings': review_settings,
            'session': self._login_user(self.settings['user']),
        }
        tools = ReviewBotTool.objects.filter(enabled=True,
                                             run_automatically=True)
        for tool in tools:
            try:
                self.celery.send_task(
                    "reviewbot.tasks.ProcessReviewRequest",
                    [payload, tool.tool_settings],
                    queue='%s.%s' % (tool.entry_point, tool.version))
            except:
                raise

    def _login_user(self, user_id):
        """
        Login as specified user, does not depend on auth backend (hopefully).

        This is based on Client.login() with a small hack that does not
        require the call to authenticate().

        Will return the session id of the login.
        """
        user = User.objects.get(id=user_id)
        user.backend = "%s.%s" % ("django.contrib.auth.backends",
                                  "ModelBackend")
        engine = import_module(settings.SESSION_ENGINE)

        # Create a fake request to store login details.
        request = HttpRequest()
        request.session = engine.SessionStore()
        login(request, user)
        request.session.save()
        return request.session.session_key

    def send_refresh_tools(self):
        """Request workers to update tool list."""
        self.celery.conf.BROKER_URL = self.settings['BROKER_URL']
        payload = {
            'url': self.settings['rb_url'],
            'session': self._login_user(self.settings['user']),
        }
        self.celery.control.broadcast('update_tools_list', payload=payload)
