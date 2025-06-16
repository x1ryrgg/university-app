import django_filters
from .models import User

class UserFilter(django_filters.FilterSet):
    role = django_filters.CharFilter(field_name='role', lookup_expr='iexact')

    class Meta:
        model = User
        fields = ()