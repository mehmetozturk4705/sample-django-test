from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Organization, OrganizationTier
from djangoTest import constants


class MockServiceResponse:
    status_code = 200


class OrganizationViewTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_organization_validations(self):
        cases = [
            # descr, payload, validation_error_keys
            ("Required fields #1", {}, ['name', 'domain']),
            ("Required fields #2", {'name': 'sample'}, ['domain']),
            ("Required fields #3", {'domain': 'sample.com'}, ['name']),
            # Max lengths
            ("Name max length", {'name': 'a' * 21, 'domain': 'sample.com'}, ['name']),
            ("Description max length", {'name': 'sample', 'description': 'a' * 201, 'domain': 'sample.com'}, ['description']),
            ("Domain max length", {'name': 'sample', 'domain': 'a' * 31}, ['domain']),
            # Specific
            ("Description forbidden character #1",
             {'name': 'sample', 'description': '<forbidden', 'domain': 'sample.com'}, ['description']),
            ("Description forbidden character #2",
             {'name': 'sample', 'description': '>forbidden', 'domain': 'sample.com'}, ['description']),

        ]
        url = '/organizations/'
        for descr, payload, validation_error_keys in cases:
            print('Testing', descr)
            response = self.client.post(url, payload)
            self.assertEqual(response.status_code, 400)
            self.assertSetEqual(set(response.json().keys()), set(validation_error_keys))

    def test_create_organization_checks_name_domain_uniqueness(self):
        payload = {'name': 'name', 'domain': 'domain'}

        url = '/organizations/'

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 201)

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.data['name'][0].code, 'unique')
        self.assertEqual(response.data['domain'][0].code, 'unique')

    def test_create_organization_removes_special_chars_from_name(self):
        # name sanitization
        url = '/organizations/'

        # Should remove - and _ chars
        response = self.client.post(url, {'name': 'sanitized-_data', 'description': 'description', 'domain': 'sample.com'})
        self.assertEqual(response.status_code, 201)

        organization_id = response.json()['id']
        organization = Organization.objects.get(id=organization_id)

        self.assertEqual(organization.name, 'sanitized  data')

    def test_create_organization_success_save(self):
        # Checks changes are saved in db.
        url = '/organizations/'
        response = self.client.post(url, {'name': 'sample', 'description': 'description', 'domain': 'sample.com'})
        self.assertEqual(response.status_code, 201)

        # Check post response
        self.assertSetEqual(
            set(response.json().keys()),
            {'id', 'name', 'domain', 'description', 'file_storage_bytes_limit', 'number_of_files_limit', 'organization_tier'}
        )

        self.assertEqual(response.json()['name'], 'sample')
        self.assertEqual(response.json()['domain'], 'sample.com')
        self.assertEqual(response.json()['description'], 'description')
        self.assertEqual(response.json()['file_storage_bytes_limit'], 2147483648)
        self.assertEqual(response.json()['number_of_files_limit'], 20)
        self.assertEqual(response.json()['organization_tier'], 'FREE')

        organization_id = response.json()['id']

        # Check fields
        organization = Organization.objects.get(id=organization_id)

        self.assertEqual(organization.name, 'sample')
        self.assertEqual(organization.description, 'description')
        self.assertEqual(organization.domain, 'sample.com')

        # Check default hydrations
        self.assertEqual(organization.file_storage_bytes_limit, 2 * constants.GB)
        self.assertEqual(organization.number_of_files_limit, 20)
        self.assertEqual(organization.organization_tier, OrganizationTier.FREE.value)

    def test_organization_available_tiers(self):
        url = '/organizations/tiers/available/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Frontend fetches this for rendering available tiers documentation.
        self.assertListEqual(response.json(), ['FREE', 'TEAM', 'ENTERPRISE'])

    def test_list_organizations(self):
        organization_instances = []
        organization_instances.append(Organization.objects.create(
            name='name1',
            description='description1',
            domain='domain1.com',
            file_storage_bytes_limit=1 * constants.MB,
            number_of_files_limit=10,
            organization_tier=OrganizationTier.FREE
        ))

        organization_instances.append(Organization.objects.create(
            name='name2',
            description='description2',
            domain='domain2.com',
            file_storage_bytes_limit=2 * constants.MB,
            number_of_files_limit=20,
            organization_tier=OrganizationTier.TEAM
        ))

        organization_instances.append(Organization.objects.create(
            name='name3',
            description='description3',
            domain='domain3.com',
            file_storage_bytes_limit=3 * constants.MB,
            number_of_files_limit=30,
            organization_tier=OrganizationTier.ENTERPRISE
        ))

        expected_response = [organization.dict() for organization in reversed(organization_instances)]

        url = '/organizations/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertListEqual(response.json(), expected_response)

    @patch('requests.post')
    def test_organization_register_success(self, mocked_post: MagicMock):
        mocked_post.return_value = MockServiceResponse()

        organization = Organization.objects.create(
            name='name1',
            description='description1',
            domain='domain1.com',
            file_storage_bytes_limit=1 * constants.MB,
            number_of_files_limit=10,
            organization_tier=OrganizationTier.FREE
        )

        url = f'/organizations/{organization.id}/register/'

        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)

        mocked_post.assert_called_once_with('https://ms.organization-registrar.company', data={'name': 'name1', 'domain': 'domain1.com'})

    @patch('requests.post')
    def test_organization_register_error(self, mocked_post: MagicMock):
        mocked_post.side_effect = ValueError

        organization = Organization.objects.create(
            name='name1',
            description='description1',
            domain='domain1.com',
            file_storage_bytes_limit=1 * constants.MB,
            number_of_files_limit=10,
            organization_tier=OrganizationTier.FREE
        )

        url = f'/organizations/{organization.id}/register/'

        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)







