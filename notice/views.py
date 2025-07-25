from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notice
from .serializers import NoticeSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class NoticeListCreateAPIView(APIView):
    def get(self, request):
        notices = Notice.objects.filter(is_active=True).order_by('-created_at')
        serializer = NoticeSerializer(notices, many=True)
        return Response({'status': 'success', 'data': serializer.data})

    def post(self, request):
        data = request.data.copy()  # Ensure we don't modify the original request data
        data['created_by'] = request.user.user_id
        serializer = NoticeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class NoticeDetailAPIView(APIView):
    def get(self, request, pk):
        notice = get_object_or_404(Notice, pk=pk)
        serializer = NoticeSerializer(notice)
        return Response({'status': 'success', 'data': serializer.data})

    def patch(self, request, pk):
        notice = get_object_or_404(Notice, pk=pk)
        serializer = NoticeSerializer(notice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Optionally: serializer.save(updated_by=request.user)
            return Response({'status': 'success', 'data': serializer.data})
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        notice = get_object_or_404(Notice, pk=pk)
        notice.delete()
        return Response({"status":"success", "message": "Notice deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
