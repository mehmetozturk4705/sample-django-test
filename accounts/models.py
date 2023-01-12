from django.db import models

# Create your models here.
from django.db.models import CheckConstraint

from djangoTest import constants


class OrganizationTier(models.TextChoices):
    FREE = 'FREE'
    INDIVIDUAL = 'INDIVIDUAL'
    TEAM = 'TEAM'
    ENTERPRISE = 'ENTERPRISE'


class Organization(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=200, null=True)
    domain = models.CharField(max_length=30, unique=True)
    file_storage_bytes_limit = models.PositiveBigIntegerField(default=2 * constants.GB)
    number_of_files_limit = models.PositiveIntegerField(default=20)
    organization_tier = models.CharField(choices=OrganizationTier.choices, max_length=10, default=OrganizationTier.FREE)

    def dict(self):
        return {
            'id': self.id, 'name': self.name, 'description': self.description,
            'domain': self.domain, 'file_storage_bytes_limit': self.file_storage_bytes_limit,
            'number_of_files_limit': self.number_of_files_limit, 'organization_tier': self.organization_tier
        }


    class Meta:
        constraints = [
            CheckConstraint(
                check=(
                    (models.Q(organization_tier=OrganizationTier.FREE) & models.Q(number_of_files_limit__lte=20)) |
                    (~models.Q(organization_tier=OrganizationTier.FREE))
                ),
                name="organization_free_limitation_constraint",
            )
            ]
