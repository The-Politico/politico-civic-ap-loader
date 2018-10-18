"""
Use this file to configure pluggable app settings and resolve defaults
with any overrides set in project settings.
"""

from django.conf import settings as project_settings

from .exceptions import AploaderConfigError


class Settings:
    pass


Settings.AUTH_DECORATOR = getattr(
    project_settings,
    "APLOADER_AUTH_DECORATOR",
    "django.contrib.auth.decorators.login_required",
)

Settings.SECRET_KEY = getattr(
    project_settings, "APLOADER_SECRET_KEY", "a-bad-secret-key"
)

Settings.AWS_ACCESS_KEY_ID = getattr(
    project_settings, "APLOADER_AWS_ACCESS_KEY_ID", None
)

Settings.AWS_SECRET_ACCESS_KEY = getattr(
    project_settings, "APLOADER_AWS_SECRET_ACCESS_KEY", None
)

Settings.AWS_REGION = getattr(project_settings, "APLOADER_AWS_REGION", None)

Settings.AWS_S3_BUCKET = getattr(
    project_settings, "APLOADER_AWS_S3_BUCKET", None
)

Settings.CLOUDFRONT_ALTERNATE_DOMAIN = getattr(
    project_settings, "APLOADER_CLOUDFRONT_ALTERNATE_DOMAIN", None
)

Settings.S3_UPLOAD_ROOT = getattr(
    project_settings, "APLOADER_S3_UPLOAD_ROOT", "uploads/aploader"
)

Settings.RESULTS_STATIC_DIR = getattr(
    project_settings, "APLOADER_RESULTS_STATIC_DIR", "static_results"
)

Settings.RESULTS_DAEMON_INTERVAL = getattr(
    project_settings, "APLOADER_RESULTS_DAEMON_INTERVAL", 10
)

Settings.DATABASE_UPLOAD_DAEMON_INTERVAL = getattr(
    project_settings, "APLOADER_DATABASE_UPLOAD_DAEMON_INTERVAL", 60
)

settings = Settings
