from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from accounts.models import Organization, OrganizationTier
from accounts.serializers import OrganizationSerializer
from djangoTest.services.storage import trigger_organization_register


class OrganizationViewSet(GenericViewSet, CreateModelMixin, ListModelMixin):
    queryset = Organization.objects.all().order_by('-id')
    serializer_class = OrganizationSerializer

    @action(methods=['get'], detail=False, url_path='tiers/available')
    def available_tiers(self, *args, **kwargs):
        return Response(
            OrganizationTier.values
        )

    @action(methods=['post'], detail=True)
    def register(self, *args, **kwargs):
        instance = self.get_object()
        try:
            trigger_organization_register(instance)
        except ValueError:
            raise PermissionDenied
        return Response(status=HTTP_204_NO_CONTENT)

