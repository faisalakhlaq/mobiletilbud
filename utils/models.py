from django.db import models
from django.utils.translation import gettext_lazy as _

class Address(models.Model):
    """Address can be used for a company or a user address.
    The address may contain a diffrent name from the user. 
    Therefore, we need the name and certain details that 
    are similar to user."""
    first_name          = models.CharField(_('First Name'), max_length=50, 
                                        blank=True, null=True)
    last_name           = models.CharField(_('Last Name'),max_length=50, 
                                        blank=True, null=True)
    title               = models.CharField(_('Title'), max_length=50, 
                                        blank=True, null=True)

    is_company          = models.BooleanField(_("Is Company"), default=False)
    company_name        = models.CharField(_('Company Name'), max_length=255, 
                                        blank=True, null=True)
    cvr                 = models.CharField(max_length=20, blank=True, null=True)
    # if it is a company so we need the contact person name
    contact_person_name = models.CharField(_("Contact Person Name"), 
                                        max_length=255, blank=True, null=True)

    street              = models.CharField(_('Street'), max_length=255, 
                                        blank=True, null=True)
    city                = models.CharField(_('City'), max_length=255, 
                                        blank=True, null=True)
    postcode            = models.CharField(_('Post Code'), max_length=50, 
                                        blank=True, null=True)
    country             = models.CharField(_('Country'), max_length=255, 
                                        blank=True, null=True)

    phone               = models.CharField(_('Phone'), max_length=50, 
                                        blank=True, null=True)
    mobile              = models.CharField(_('Mobile'), max_length=50, 
                                        blank=True, null=True)
    email               = models.EmailField(_('Email'), blank=True, null=True)

    def get_full_name(self):
        """
        Returns the full name.
        """
        return u'{0} {1}'.format(self.first_name, self.last_name)

    def get_address(self):
        """Returns the complete address - Street, postcode, city, country"""
        return u'{0}, {1} {2}, {3}'.format(
            self.street, self.postcode, self.city, self.country)

    def __str__(self):
        try:
            return "{0} {1} {2}".format(
                self.first_name, self.last_name, self.email)
        except Exception as e:
            print(e)
            return "No Name"
