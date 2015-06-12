from rest_framework import status, generics
from rest_framework.response import Response

from apps.taxonomy.serializers.taxon_search import BaseSearchSerializer, \
    CommonNameSearchSerializer
from apps.taxonomy.models import CommonName


class BaseSearchView(generics.ListAPIView):
    model = CommonName

    def get(self, request, **kwargs):
        model = self.model
        serializer = BaseSearchSerializer(data=request.GET, model=model)
        if serializer.is_valid():
            search_result = serializer.search()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(search_result)


class CommonNameSearchView(generics.ListAPIView):
    model = CommonName

    def get(self, request, **kwargs):
        model = self.model
        serializer = CommonNameSearchSerializer(data=request.GET, model=model)
        if serializer.is_valid():
            search_result = serializer.search()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(search_result)
