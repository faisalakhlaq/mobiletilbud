from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from .utils import unique_slug_generator

class TelecomCompany(models.Model):
    """Telecom company that provides the telecom services.
        In our case we are interested in storing companies
        which sales mobile phones with their monthly call 
        packages."""
    name            = models.CharField(_("Name"), max_length=50)
    slug            = models.SlugField(_("slug"), blank=True, null=True)

    class Meta:
        verbose_name = _("Telecom Company")
        verbose_name_plural = _("Telecom Companies")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("telecomcompany_detail", kwargs={"slug": self.slug})


class Country(models.Model):
    """Country model will save the countries for a telecom
       company. One company can be operating in different
       countries."""
    name                    = models.CharField(_("Country Name"), max_length=80)
    telecom_company         = models.ManyToManyField("TelecomCompany")

    def __str__(self):
        return self.name


# class Package(models.Model):
#     """Subscription / Package is monthly phone subscription provided 
#     and charged by a Telecom Company. It can be refered to as call 
#     and data package. There can be different call and data packages. 
#     Prices for mobile phones vary depending on the package s/he chooses.
#     """
#     slug                    = models.SlugField(_("slug"))
#     telecom_company         = models.ForeignKey("TelecomCompany", 
#                               verbose_name=_("Telecom Company"), 
#                               on_delete=models.CASCADE)
#     monthly_charges         = models.FloatField(_("Monthly Charges"))
#     # Mobile data is the amount of data provided on a monthly base. 
#     # 500 MB, 5 GB
#     mobile_data             = models.CharField(_("Mobile Data"), 
#                               blank=True, null=True, max_length=50)
#     data_in_other_countries = models.CharField(_("Data in other countries"), 
#                               blank=True, null=True, max_length=50)
#     for_young               = models.BooleanField(_("For Young People"),
#                               default=False)
#     class Meta:
#         unique_together = (
#             ('monthly_charges', 'telecom_company', 'for_young')
#         )
#         verbose_name = _("Package")
#         verbose_name_plural = _("Packages")

#     def __str__(self):
#         return self.name

#     def get_absolute_url(self):
#         return reverse("package_detail", kwargs={"slug": self.slug})


# class MobilePrice(models.Model):
#     """Mobile phone price depends on:
#        1. Telecom company,
#        2. Package,
#        3. Mobile Variation 
#        Therefore, we store everything in one place to
#        have different price of the same mobile phone."""
#     mobile              = models.ForeignKey("Mobile", 
#                           verbose_name=_("Mobile"), 
#                           on_delete=models.CASCADE)
#     # prices will vary based on variation e.g. mobile memory, color
#     mobile_variations   = models.ManyToManyField(MobileVariation)
#     telecom_company     = models.ForeignKey("TelecomCompany", 
#                           verbose_name=_("Telecom Company"), 
#                           on_delete=models.CASCADE)
#     package             = models.ForeignKey("Package", 
#                                 verbose_name=_("Package"), 
#                                 on_delete=models.CASCADE)
#     # Mobile phone cash price as per telecom company 
#     # irrespective of the package
#     cash_price          = models.FloatField(_("price"))
#     # Monthly price in 6 months according to company and package 
#     price_6_months      = models.FloatField(_("6 months price"), 
#                           blank=True, null=True)
#     price_12_months     = models.FloatField(_("12 months price"),
#                           blank=True, null=True)
#     price_24_months     = models.FloatField(_("24 months price"),
#                           blank=True, null=True)
#     price_36_months     = models.FloatField(_("36 months price"),
#                           blank=True, null=True)
#     price_40_months     = models.FloatField(_("40 months price"),
#                           blank=True, null=True)
#     slug                = models.SlugField(_("slug"))

#     class Meta:
#         verbose_name = _("Mobile Price")
#         verbose_name_plural = _("Mobile Prices")

#     def __str__(self):
#         return str(self.price)

#     def get_absolute_url(self):
#         return reverse("mobile_price", kwargs={"pk": self.pk})


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance=instance)

# pre_save.connect(pre_save_receiver, sender=Mobile)
pre_save.connect(pre_save_receiver, sender=TelecomCompany)
