from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError as RestFrameworkValidationError

from care.emr.models.consent import Consent
from care.emr.models.encounter import Encounter
from care.emr.models.tag_config import TagConfig
from care.emr.resources.tag.config_spec import TagResource
from care.emr.tagging.base import SingleFacilityTagManager
from care_auto_tag.settings import plugin_settings as settings


@receiver(post_save, sender=Encounter)
def add_missing_consent_tag(sender, instance: Encounter, created: bool, **kwargs):
    if not created:
        return

    if not instance.consents.exists():
        tag_manager = SingleFacilityTagManager()
        try:
            tag_manager.set_tags(
                TagResource.encounter,
                instance,
                [settings.AUTO_TAG_MISSING_CONSENT_TAG_ID],
                instance.created_by,
                instance.facility,
            )
        except ValueError as e:
            raise RestFrameworkValidationError(str(e)) from e


@receiver(post_save, sender=Consent)
def remove_missing_consent_tag(sender, instance: Consent, created: bool, **kwargs):
    if not created:
        return

    tag_config = TagConfig.objects.filter(
        external_id=settings.AUTO_TAG_MISSING_CONSENT_TAG_ID
    ).first()
    if not tag_config:
        return

    encounter = instance.encounter
    if tag_config.id in encounter.tags:
        tag_manager = SingleFacilityTagManager()
        try:
            tag_manager.unset_tags(
                encounter,
                [settings.AUTO_TAG_MISSING_CONSENT_TAG_ID],
                encounter.created_by,
            )
        except ValueError as e:
            raise RestFrameworkValidationError(str(e)) from e
