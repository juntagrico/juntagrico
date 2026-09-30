from debug_toolbar.settings import PANELS_DEFAULTS

from .dev import *  # noqa: F401,F403

# Core Settings

DEBUG = True

INSTALLED_APPS += ('debug_toolbar', 'template_profiler_panel', 'django_admin_shell')  # noqa: F405

ROOT_URLCONF = 'urls.debug'

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405

INTERNAL_IPS = [
    "127.0.0.1",
]

DEBUG_TOOLBAR_PANELS = PANELS_DEFAULTS + [
    "template_profiler_panel.panels.template.TemplateProfilerPanel",
]
