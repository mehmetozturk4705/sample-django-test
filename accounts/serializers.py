from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from accounts.models import Organization, OrganizationTier


class OrganizationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=20, validators=[UniqueValidator(queryset=Organization.objects.all())])
    domain = serializers.CharField(max_length=30, validators=[UniqueValidator(queryset=Organization.objects.all())])
    description = serializers.CharField(required=False, max_length=200)
    file_storage_bytes_limit = serializers.IntegerField(read_only=True)
    number_of_files_limit = serializers.IntegerField(read_only=True)
    organization_tier = serializers.ChoiceField(choices=OrganizationTier.choices, read_only=True)

    def validate_description(self, value):
        if {'<', '>'}.intersection(set(value)):
            raise ValidationError('Description cannot have < or >')
        return value

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        # Sanitize data
        data['name'] = data['name'].replace('-', ' ').replace('_', ' ')
        return data

    class Meta:
        fields = ['id', 'name', 'domain', 'description', 'file_storage_bytes_limit', 'number_of_files_limit', 'organization_tier']
        model = Organization
