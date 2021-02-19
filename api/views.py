from rest_framework import status, generics, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from telecompanies.models import Offer
from mobiles.models import Mobile
from api.serializers import OfferSerializer, MobileSerializer

class TilbudView(
    generics.GenericAPIView, 
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
