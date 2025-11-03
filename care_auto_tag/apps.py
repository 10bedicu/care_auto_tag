import logging

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _

from care_auto_tag.settings import PLUGIN_NAME
from care_auto_tag.settings import plugin_settings as settings

logger = logging.getLogger(__name__)


class CareAutoTagConfig(AppConfig):
    name = PLUGIN_NAME
    verbose_name = _("Care Auto Tag")

    def ready(self):
        if not settings.AUTO_TAG_MISSING_CONSENT_TAG_ID:
            logger.warning(
                "Skipping signal registration as AUTO_TAG_MISSING_CONSENT_TAG_ID is not set"
            )
        else:
            import care_auto_tag.signals.manage_missing_consent_tag  # noqa: F401

        def init_missing_consent_tag_config(**kwargs):
            if not settings.AUTO_TAG_MISSING_CONSENT_TAG_ID:
                logger.warning(
                    "Skipping 'Missing consent' tag config initialization as AUTO_TAG_CONSENT_MISSING_TAG_ID is not set"
                )
                return

            from care.emr.models.tag_config import TagConfig
            from care.emr.resources.tag.config_spec import (
                TagCategoryChoices,
                TagResource,
                TagStatus,
            )

            missing_consent_tag = TagConfig.objects.filter(
                external_id=settings.AUTO_TAG_MISSING_CONSENT_TAG_ID
            ).first()

            if (
                missing_consent_tag
                and missing_consent_tag.meta.get("owner") != "care_auto_tag"
            ):
                logger.error(
                    "Tag config with external_id {settings.AUTO_TAG_MISSING_CONSENT_TAG_ID} already exists, please change the external_id"
                )
                raise ValueError(
                    "Tag config with external_id {settings.AUTO_TAG_MISSING_CONSENT_TAG_ID} already exists, please change the external_id"
                )

            instance, created = TagConfig.objects.update_or_create(
                external_id=settings.AUTO_TAG_MISSING_CONSENT_TAG_ID,
                defaults={
                    "category": TagCategoryChoices.advance_directive,
                    "resource": TagResource.encounter,
                    "status": TagStatus.active,
                    "display": "Missing Consent",
                    "description": "This is a system generated tag to tag encounters that do not have a consent",
                    "priority": 1,
                    "meta": {"owner": "care_auto_tag", "color": "#e7000b"},
                },
            )
            action = "created" if created else "updated"
            logger.info(
                "Missing Consent tag config %s (external_id=%s)",
                action,
                str(instance.external_id),
            )

        post_migrate.connect(init_missing_consent_tag_config, sender=self)
