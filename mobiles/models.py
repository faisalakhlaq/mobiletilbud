from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from core.utils import unique_slug_generator


class MobileBrand(models.Model):
    """Represents the mobile manufacturers"""
    name            = models.CharField(_("Name"), max_length=50)
    # Image icon of the manufacturer
    image           = models.ImageField(_("Image"), upload_to='mobile_brands/',
                                blank=True, null=True)

    def __str__(self):
        return self.name
    
    # def get_absolute_url(self):
    #     return reverse("mobile_detail", kwargs={"slug": self.name})

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
    launch_date             = models.DateField(_("Launch Date"), 
                                  auto_now=False, auto_now_add=False,
                                  blank=True, null=True)

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
                                  on_delete=models.CASCADE, 
                                  related_name='technical_specs')
    two_g                       = models.BooleanField(blank=True, null=True)
    three_g                     = models.BooleanField(blank=True, null=True) 
    four_g                      = models.BooleanField(blank=True, null=True)
    five_g                      = models.BooleanField(blank=True, null=True)
    WiFi                        = models.BooleanField(blank=True, null=True)
    dual_sim                    = models.BooleanField(blank=True, null=True)
    dimensions                  = models.CharField(_("Dimensions"), 
                                  max_length=255, blank=True, null=True)
    weight                      = models.CharField(_("Weight"), 
                                  max_length=255, blank=True, null=True)
    screen_type                 = models.CharField(_("Screen Type"), 
                                  max_length=255, blank=True, null=True)
    screen_size                 = models.CharField(_("Screen Size"), 
                                  max_length=255, blank=True, null=True)
    screen_resolution           = models.CharField(_("Screen Resolution"), 
                                  max_length=255, blank=True, null=True)
    ip_certification            = models.CharField(_("IP Certification"), 
                                  max_length=255, blank=True, null=True)
    internal_storage            = models.CharField(_("Internal Storage"), 
                                  max_length=255, blank=True, null=True)
    external_storage            = models.CharField(_("External Storage"), 
                                  max_length=255, blank=True, null=True)
    WLAN                        = models.CharField(_("WLAN"), 
                                  max_length=255, blank=True, null=True)
    bluetooth                   = models.CharField(_("Bluetooth"), 
                                  max_length=255, blank=True, null=True)
    NFC                         = models.BooleanField(default=False)
    USB                         = models.CharField(_("USB"), 
                                  max_length=255, blank=True, null=True)
    battery_type                = models.CharField(_("Battery Type"), 
                                  max_length=255, blank=True, null=True)
    wireless_charging           = models.CharField(_("Wireless Charging"), 
                                  max_length=255, blank=True, null=True)
    fast_charging               = models.CharField(_("Fast Charging"), 
                                  max_length=255, blank=True, null=True)
    chipset                     = models.CharField(_("Chipset"), 
                                  max_length=255, blank=True, null=True)
    operating_system            = models.CharField(_("Operating System"), 
                                  max_length=255, blank=True, null=True)
    ram                         = models.CharField(_("RAM"), 
                                  max_length=255, blank=True, null=True)
    launch                      = models.CharField(_("Launch"), 
                                  max_length=255, blank=True, null=True)
    status                      = models.CharField(_("Status"), 
                                  max_length=255, blank=True, null=True)
    def __str__(self):
        return self.mobile.name


class MobileCameraSpecification(models.Model):
    mobile                      = models.ForeignKey("Mobile", 
                                  on_delete=models.CASCADE,
                                  related_name='camera_specs')
    rear_cam_lenses             = models.IntegerField(_("rear_camera_lenses"), 
                                  blank=True, null=True)
    rear_cam_megapixel          = models.CharField(_("rear_camera_megapixel"), 
                                  max_length=255, blank=True, null=True)
    back_cam_aperture           = models.CharField(_("Rear Camera Aperture"), 
                                  max_length=50, blank=True, null=True)
    rear_cam_video_resolution   = models.CharField(_("rear_camera_video_resolution"), 
                                  max_length=50, blank=True, null=True)
    front_cam_lenses            = models.IntegerField(_("front_camera_lenses"),
                                  blank=True, null=True)
    front_cam_megapixel         = models.CharField(_("front_camera_megapixel"), 
                                  max_length=255, blank=True, null=True)
    front_cam_aperture          = models.CharField(_("front_camera_aperture"), 
                                  max_length=50, blank=True, null=True)
    front_cam_video_resolution  = models.CharField(_("front_camera_video_resolution"), 
                                  max_length=50, blank=True, null=True) 

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
    value       = models.CharField(_("value"), max_length=255)  # S, M, L
    # attachment = models.ImageField(blank=True)

    class Meta:
        unique_together = (
            ('variation', 'value')
        )
    def __str__(self):
        return self.value

class PopularMobile(models.Model):
    mobile = models.OneToOneField(
        'Mobile',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    def get_absolute_url(self):
        return self.mobile.get_absolute_url()
    
    def __str__(self):
        return self.mobile.name


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance=instance)
    delete_image(sender, instance, args, kwargs)

def delete_image(sender, instance, *args, **kwargs):
    """If the image for the given object is updated, 
    then delete the previous one."""
    try:
        Klass = instance.__class__
        old_image = Klass.objects.get(pk=instance.pk).image
        if not old_image:
            return
        new_image_url = None
        if instance.image:
            new_image_url = instance.image.url
        if old_image and old_image.url != new_image_url:
            old_image.delete(save=False)
    except Klass.DoesNotExist:
        return

pre_save.connect(pre_save_receiver, sender=Mobile)
pre_save.connect(delete_image, sender=MobileBrand)
