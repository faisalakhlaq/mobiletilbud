from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import TelecomCompany
from mobiles.models import Mobile, MobileBrand
from telecompanies.models import Offer

class OfferSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Offer
        fields = '__all__'

class TelecompanySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TelecomCompany
        fields = '__all__'

class MobileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mobile
        fields = '__all__'

class MobileBrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = MobileBrand
        fields = '__all__'
