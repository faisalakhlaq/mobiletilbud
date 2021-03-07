from rest_framework import status, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (OfferSerializer, MobileSerializer, 
CreatePartnerEmployeeSerializer, PartnerLoginSerializer)
from api.permissions import IsEmployeeOfCompany
from mobiles.models import Mobile
from partners.models import PartnerEmployee
from telecompanies.models import Offer


class TilbudView(
    GenericAPIView, 
    mixins.ListModelMixin, 
    mixins.RetrieveModelMixin
    ):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()
    lookup_field = 'id'

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            return self.retrieve(request)
        else:
            return self.list(request)

class TilbudDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return Offer.objects.get(id=id)
        except Offer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
 
    def get(self, request, id):
        obj = self.get_object(id)
        serializer = OfferSerializer(obj)
        return Response(serializer.data)

class MobileListAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mobiles = Mobile.objects.all()
        serializer = MobileSerializer(mobiles, many=True)
        return Response(serializer.data)

class MobileDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        try:
            return Mobile.objects.get(id=id)
        except Mobile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
 
    def get(self, request, id):
        obj = self.get_object(id)
        serializer = MobileSerializer(obj)
        return Response(serializer.data)


class RegisterPartnerEmployeeView(GenericAPIView):
    serializer_class = CreatePartnerEmployeeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        return Response(data=data, status=status.HTTP_201_CREATED)

class PartnerLoginAPIView(GenericAPIView):
    serializer_class = PartnerLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class CreateTilbudAPI(ListCreateAPIView):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated, IsEmployeeOfCompany]

    def get_queryset(self):
        try:
            employee = PartnerEmployee.objects.get(user=self.request.user)
            return self.queryset.filter(telecom_company=employee.company)
        except PartnerEmployee.DoesNotExist:
            return [] # if the user is not an employee then return empty list

    def perform_create(self, serializer):
        try:
            # import pdb; pdb.set_trace()
            employee = PartnerEmployee.objects.get(user=self.request.user)
            if not employee.company == serializer.validated_data['telecom_company']:
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
            return serializer.save()
        except PartnerEmployee.DoesNotExist:
                return Response(data=None, status=status.HTTP_403_FORBIDDEN)
