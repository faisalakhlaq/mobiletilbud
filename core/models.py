from django.db import models
from django.utils.translation import gettext_lazy as _


class MobileBrand(models.Model):
    """Represents the mobile manufacturers"""
    name            = models.CharField(_("name"), max_length=50)    

    def __str__(self):
        return self.name

class Mobile(models.Model):
    name                        = models.CharField(_("name"), max_length=50)
    brand                       = models.ForeignKey("MobileBrand", 
                                  verbose_name=_("Brand"), 
                                  on_delete=models.SET_NULL, 
                                  null=True, blank=True)
    cash_price                  = models.FloatField(_("Cash Price"), 
                                  blank=True, null=True)    
    slug                        = models.SlugField(_("slug"))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("mobile_detail", kwargs={"slug": self.slug})


class MobileTechnicalSpecification(models.Model):
    mobile                      = models.ForeignKey("Mobile", 
                                  on_delete=models.CASCADE)
    two_g                       = models.BooleanField()
    three_g                     = models.BooleanField() 
    four_g                      = models.BooleanField()
    five_g                      = models.BooleanField()
    WiFi                        = models.BooleanField()
    taleVoLTE                   = models.BooleanField()
    dual_sim                    = models.BooleanField()
    dimensions                  = models.CharField(_("dimensions"), 
                                  max_length=50)
    weight                      = models.CharField(_("weight"), 
                                  max_length=10)
    screen_type                 = models.CharField(_("screen_type"), 
                                  max_length=50)
    screen_size                 = models.CharField(_("screen_size"), 
                                  max_length=10)
    screen_resolution           = models.CharField(_("screen_resolution"), 
                                  max_length=30)
    ip_certification            = models.CharField(_("ip_certification"), 
                                  max_length=10)
    internal_storage            = models.CharField(_("internal_storage"), 
                                  max_length=10)
    external_storage            = models.CharField(_("external_storage"), 
                                  max_length=10)
    WLAN                        = models.CharField(_("WLAN"), 
                                  max_length=10)
    bluetooth                   = models.CharField(_("bluetooth"), 
                                  max_length=30)
    NFC                         = models.BooleanField(default=True)
    USB                         = models.CharField(_("USB"), 
                                  max_length=10)
    wireless_charging           = models.CharField(_("wireless_charging"), 
                                  max_length=30)
    fast_charging               = models.CharField(_("fast_charging"), 
                                  max_length=30)
    chipset                     = models.CharField(_("chipset"), 
                                  max_length=30)
    control_system              = models.CharField(_("control_system"), 
                                  max_length=30)

    def __str__(self):
        return self.mobile.name


class MobileCameraSpecification(models.Model):
    mobile                      = models.ForeignKey("Mobile", 
                                  on_delete=models.CASCADE)
    rear_cam_lenses             = models.IntegerField(_("rear_camera_lenses"))
    rear_cam_megapixel          = models.CharField(_("rear_camera_megapixel"), 
                                  max_length=30)
    back_cam_aperture           = models.CharField(_("rear_camera_megapixel"), 
                                  max_length=30)
    rear_cam_video_resolution   = models.CharField(_("rear_camera_video_resolution"), 
                                  max_length=30)
    front_cam_lenses            = models.IntegerField(_("front_camera_lenses"))
    front_cam_megapixel         = models.CharField(_("front_camera_megapixel"), 
                                  max_length=30)
    front_cam_aperture          = models.CharField(_("front_camera_aperture"), 
                                  max_length=30)
    front_cam_video_resolution  = models.CharField(_("front_camera_video_resolution"), 
                                  max_length=30) 

    def __str__(self):
        return self.mobile.name

    
class Variation(models.Model):
    """Store different variations of a mobile device. e.g. 
       Variation on color, memory. Price is dependent on variation
       """
    name            = models.CharField(_("Name"), max_length=50)
    mobile          = models.ForeignKey("Mobile", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class MobileVariation(models.Model):
    """Store the actual values for each variation. e.g. Color of a 
    mobile can be blue, red, green. Memory can be 32, 64, 128."""
    variation   = models.ForeignKey(Variation, on_delete=models.CASCADE)
    value       = models.CharField(_("value"), max_length=50)  # S, M, L
    # attachment = models.ImageField(blank=True)

    class Meta:
        unique_together = (
            ('variation', 'value')
        )

    def __str__(self):
        return self.value


class TelecomCompany(models.Model):
    """Telecom company that provides the telecom services.
        In our case we are interested in storing companies
        which sales mobile phones with their monthly call 
        packages."""
    name            = models.CharField(_("Name"), max_length=50)
    slug            = models.SlugField(_("slug"))
    
    class Meta:
        verbose_name = _("Telecom Company")
        verbose_name_plural = _("Telecom Companies")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("telecomcompany_detail", kwargs={"slug": self.slug})


class Package(models.Model):
    """Package is monthly phone subscription provided and charged 
    by a Telecom Company. It can be refered to as call and data package.
    There can be different call and data packages. Prices for 
    mobile phones vary depending on the package s/he chooses.
    """
    slug                    = models.SlugField(_("slug"))
    telecom_company         = models.ForeignKey("TelecomCompany", 
                                verbose_name=_("Telecom Company"), 
                                on_delete=models.CASCADE)
    monthly_charges         = models.FloatField(_("Monthly Charges"))
    # Mobile data is the amount of data provided on a monthly base. 
    # 500 MB, 5 GB
    mobile_data             = models.CharField(_("Mobile Data"), 
                              blank=True, null=True, max_length=50)
    data_in_other_countries = models.CharField(_("Data in other countries"), 
                              blank=True, null=True, max_length=50)

    class Meta:
        verbose_name = _("Package")
        verbose_name_plural = _("Packages")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("package_detail", kwargs={"slug": self.slug})


class MobilePrice(models.Model):
    """Mobile phone price depends on:
       1. Telecom company,
       2. Package,
       3. Mobile Variation 
       Therefore, we store everything in one place to
       have different price of the same mobile phone."""
    mobile              = models.ForeignKey("Mobile", 
                          verbose_name=_("Mobile"), 
                          on_delete=models.CASCADE)
    package             = models.ForeignKey("Package", 
                                verbose_name=_("Package"), 
                                on_delete=models.CASCADE)
    # Mobile phone cash price as per telecom company 
    # irrespective of the package
    cash_price          = models.FloatField(_("price"))
    # Monthly price in 6 months according to company and package 
    price_6_months      = models.FloatField(_("price"))
    price_12_months     = models.FloatField(_("price"))
    price_24_months     = models.FloatField(_("price"))
    price_36_months     = models.FloatField(_("price"))
    slug                = models.SlugField(_("slug"))

    class Meta:
        verbose_name = _("MobilePrice")
        verbose_name_plural = _("MobilePrices")

    def __str__(self):
        return str(self.price)

    def get_absolute_url(self):
        return reverse("mobile_price", kwargs={"pk": self.pk})
    # TODO prices according to the mobile variation