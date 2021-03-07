from rest_framework.permissions import BasePermission

from partners.models import PartnerEmployee


class IsEmployeeOfCompany(BasePermission):
    """Check if the current user is the 
    employee of a given company."""

    def has_object_permission(self, request, view, obj):
        try:
            employee = PartnerEmployee.objects.get(user=request.user)
            return obj.telecom_company == employee.company
        except PartnerEmployee.DoesNotExist:
            return False
        