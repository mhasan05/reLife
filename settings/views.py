# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SiteInfoModel
from .serializers import SiteInfoSerializer
from django.shortcuts import get_object_or_404

class SiteInfoListCreateAPIView(APIView):
    def get(self, request):
        site_infos = SiteInfoModel.objects.all()
        serializer = SiteInfoSerializer(site_infos, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request):
        site_info = SiteInfoModel.objects.first()
        if not site_info:
            return Response({"status": "error", "message": "No SiteInfoModel found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SiteInfoSerializer(site_info, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success update", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


