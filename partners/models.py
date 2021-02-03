from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TelecomCompany
from utils.models import Address

User = settings.AUTH_USER_MODEL

class PartnerEmployee(models.Model):
    """This is a special user who is representing a company.
    This user will be able to login to a form and add their products.
    The products should come unders the model.Item. Supplier can
    edit, update, delete and add new items only for its company."""
    user                = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date          = models.DateField(null=True, blank=True)
    image               = models.ImageField(_("Picture"), 
                            upload_to='profile_images/', 
                            null=True, blank=True)
    company             = models.ForeignKey(TelecomCompany, 
                            verbose_name=_("Company"), 
                            related_name='partner_employee', 
                            on_delete=models.SET_NULL,
                            blank=True, null=True)
    address             = models.ForeignKey(Address, 
                            verbose_name=_("Partner Employee Address"), 
                            related_name='partner_employee', 
                            on_delete=models.SET_NULL, 
                            blank=True, null=True)

    class Meta:
        verbose_name = _("Partner Employee")
        verbose_name_plural = _("Partner Employees")

    def __str__(self):
        return self.user.name

    def get_absolute_url(self):
        return reverse("partners:partner_employee_detail", kwargs={"pk": self.pk})
