from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import fields
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from core.models import TelecomCompany
from mobiles.models import Mobile, MobileBrand
from partners.models import PartnerEmployee
from telecompanies.models import Offer
from utils.models import Address


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


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=50, 
        min_length=6, 
        write_only=True
        )
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        return super().create(validated_data)
    
    def validate(self, validated_data):
        return super().validate(validated_data)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class CreatePartnerEmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    address = AddressSerializer()

    class Meta:
        model = PartnerEmployee
        fields=['user', 'image', 'company', 'address',]

    def create(self, validated_data):
        user_data = validated_data.get('user', {})
        user = self.fields['user'].__class__(data=user_data)
        user.is_valid()
        user = user.create(validated_data=user_data)
        user.set_password(user_data['password'])
        user.is_active = False
        user.save()
        address_data = validated_data.get('address', {})
        address = self.fields['address'].__class__(data=address_data)
        if not self.is_empty_address(address):
            address.is_valid()
            address.save()
            address = address.instance
        else:
            address = None
        partner_employee = PartnerEmployee.objects.create(
            user=user,
            company=validated_data['company'],
            address=address,
            image=validated_data['image']
        )
        return partner_employee

    def validate(self, validated_data):
        user_data = validated_data.get('user', {})
        username = user_data.get('username', '')
        if not username:
            raise serializers.ValidationError({
                'username': [_('Please provide a username.')]})
        first_name = user_data.get('first_name', '')
        if not first_name:
            raise serializers.ValidationError({
                'first_name': [_("First name cannot be empty")]})
        last_name = user_data.get('last_name', '')
        if not last_name:
            raise serializers.ValidationError({
                'last_name': [_("Last name cannot be empty")]})
        email = user_data.get('email', '')
        if not email:
            raise serializers.ValidationError({
                'email': [_("Email cannot be empty")]})
        password = user_data.get('password', '')
        if not password:
            raise serializers.ValidationError({
                'password': [_("Password cannot be empty")]})
        image = validated_data.get('image', '')
        if not image:
            raise serializers.ValidationError({
                'image': [_("Image cannot be empty")]})
        company = validated_data.get('company', '')
        if not company:
            raise serializers.ValidationError({
                'company': [_("Company cannot be empty")]})
        return super().validate(validated_data)

    def is_empty_address(self, address_serializer):
        """Check if there is any data for the address 
        fields in the address serializer. If there is 
        no data then the address is empty and return True. 
        Otherwie returns False."""
        address_serializer.is_valid()
        address_ = address_serializer.validated_data
        if address_['first_name']: 
            return False
        elif address_['last_name']: 
            return False
        elif address_['title']: 
            return False
        elif address_['is_company']: 
            return False
        elif address_['company_name']: 
            return False
        elif address_['cvr']: 
            return False
        elif address_['contact_person_name']: 
            return False
        elif address_['street']: 
            return False
        elif address_['city']: 
            return False
        elif address_['postcode']: 
            return False
        elif address_['country']: 
            return False
        elif address_['phone']: 
            return False
        elif address_['mobile']: 
            return False
        elif address_['email']: 
            return False 
        
        return True

class PartnerLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=1)
    password = serializers.CharField(
        max_length=50, 
        min_length=6, 
        write_only=True
        )
    class Meta:
        model = PartnerEmployee
        fields = ('username', 'password')

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed({
                'email': [_("Sorry! Unable to login. Invalid credentials or inactive / disabled user. Please contact admin.")]})
        # if not user.is_active:
        #     raise AuthenticationFailed({
        #         'email': [_("Sorry! Unable to login. Inactive / disabled user. \
        #         Please contact admin.")]})
        data = {
            'username': user.username, 
            'first name': user.first_name,
            'email': user.email,
            }
        return data
