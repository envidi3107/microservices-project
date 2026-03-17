from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recommendation
from .serializers import RecommendationSerializer

class RecommendationListCreate(APIView):
    def get(self, request):
        recommendations = Recommendation.objects.all()
        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecommendationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecommendationDetail(APIView):
    def get_object(self, pk):
        try:
            return Recommendation.objects.get(pk=pk)
        except Recommendation.DoesNotExist:
            return None

    def get(self, request, pk):
        recommendation = self.get_object(pk)
        if recommendation is None:
            return Response({"error": "Recommendation not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RecommendationSerializer(recommendation)
        return Response(serializer.data)

    def put(self, request, pk):
        recommendation = self.get_object(pk)
        if recommendation is None:
            return Response({"error": "Recommendation not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RecommendationSerializer(recommendation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recommendation = self.get_object(pk)
        if recommendation is None:
            return Response({"error": "Recommendation not found"}, status=status.HTTP_404_NOT_FOUND)
        recommendation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
