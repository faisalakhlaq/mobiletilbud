from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from core.utils import unique_slug_generator


class MobileBrand(models.Model):
    """Represents the mobile manufacturers"""
    name            = models.CharField(_("Name"), max_length=50)
    def __str__(self):
        return self.name
    
    # def get_absolute_url(self):
    #     return reverse("mobile_detail", kwargs={"slug": self.name})

#TODO make sure the image is deleted on deleting the record
class Mobile(models.Model):
    name                    = models.CharField(_("name"), max_length=50)
    # full name will be Brand name + name
    full_name               = models.CharField(_("Full Name"), max_length=50, 
                                  blank=True, null=True)
    brand                   = models.ForeignKey('MobileBrand', 
                                  verbose_name=_("Brand"),
                                  related_name=_("mobiles"),
                                  on_delete=models.SET_NULL, 
                                  null=True, blank=True)
    cash_price              = models.FloatField(_("Cash Price"), 
                                  blank=True, null=True)    
    slug                    = models.SlugField(_("slug"), unique=True,
                                  blank=True, null=True)
    image                   = models.ImageField(_("Image"), upload_to='mobiles/',
                                  blank=True, null=True)
    # url for the mobile on a website for further details of the mobile                              
    url                     = models.URLField("Url", blank=True, null=True)

    class Meta:
        unique_together = (
            ('name', 'brand')
        )

    def __str__(self):
        if self.full_name:
            return self.full_name
        return self.name
    def get_absolute_url(self):
        return reverse("mobiles:mobile-detail", kwargs={"slug": self.slug})


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
    ram                         = models.CharField(_("RAM"), 
                                  max_length=10, blank=True, null=True)

    def __str__(self):
        return self.mobile.name


class MobileCameraSpecification(models.Model):
    mobile                      = models.ForeignKey("Mobile", 
                                  on_delete=models.CASCADE)
    rear_cam_lenses             = models.IntegerField(_("rear_camera_lenses"))
    rear_cam_megapixel          = models.CharField(_("rear_camera_megapixel"), 
                                  max_length=30)
    back_cam_aperture           = models.CharField(_("Rear Camera Aperture"), 
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

    class Meta:
        unique_together = (
            ('name', 'mobile')
        )
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


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance=instance)

pre_save.connect(pre_save_receiver, sender=Mobile)
