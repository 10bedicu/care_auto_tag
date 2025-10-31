import logging

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from care.emr.resources.tag.config_spec import (
    TagCategoryChoices,
    TagResource,
    TagStatus,
)
from care_auto_tag.settings import PLUGIN_NAME
from care_auto_tag.settings import plugin_settings as settings

logger = logging.getLogger(__name__)


class CareAutoTagConfig(AppConfig):
    name = PLUGIN_NAME
    verbose_name = _("Care Auto Tag")

    def ready(self):
        from care.emr.models.tag_config import TagConfig

        if settings.AUTO_TAG_MISSING_CONSENT_TAG_ID:
            missing_consent_tag = TagConfig.objects.filter(
                external_id=settings.AUTO_TAG_MISSING_CONSENT_TAG_ID
            ).first()

            if (
                missing_consent_tag
                and missing_consent_tag.meta.get("owner") != "care_auto_tag"
            ):
                logger.error(
                    "Tag with external_id {settings.AUTO_TAG_MISSING_CONSENT_TAG_ID} already exists, please change the external_id"
                )
                raise ValueError(
                    "Tag with external_id {settings.AUTO_TAG_MISSING_CONSENT_TAG_ID} already exists, please change the external_id"
                )

            if not missing_consent_tag:
                TagConfig.objects.create(
                    external_id=settings.AUTO_TAG_MISSING_CONSENT_TAG_ID,
                    category=TagCategoryChoices.advance_directive,
                    description="This is a system generated tag to tag encounters that do not have a consent",
                    display="Missing Consent",
                    priority=1,
                    resource=TagResource.encounter,
                    status=TagStatus.active,
                    meta={"owner": "care_auto_tag", "variant": "danger"},
                )

            import care_auto_tag.signals.manage_missing_consent_tag  # noqa F401

        else:
            logger.warning(
                "Skipping 'Missing consent' tag initialization as AUTO_TAG_CONSENT_MISSING_TAG_ID is not set"
            )
