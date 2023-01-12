from django.db import IntegrityError
from django.test import TransactionTestCase

from accounts.models import Organization


class OrganizationModelTestCase(TransactionTestCase):
    def test_free_organizations_can_have_20_file_limit(self):
        # Based on ISSUE-21 Free tiered organizations cannot have more than 20 file limit
        # accounts microservice relies on this setting.
        with self.assertRaises(IntegrityError,) as ctx:
            Organization.objects.create(
                name="Sample",
                domain="sample.com",
                number_of_files_limit = 21
            )

        self.assertTrue('organization_free_limitation_constraint' in str(ctx.exception))