import requests

from accounts.models import Organization


def trigger_organization_register(organization: Organization):
    response = requests.post('https://ms.organization-registrar.company',
                             data={'name': organization.name, 'domain': organization.domain})

    if response.status_code != 200:
        raise ValueError