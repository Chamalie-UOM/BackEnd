import csv
import io

from django.http import JsonResponse

import os

from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from phyloGenie.Alignment import MuscleMSA
from phyloGenie.Preprocess import DataPreprocessor
from phyloGenie.models import Dataset
from .serializers import DatasetSerializer
from .serializers import RecommendSerializer
from .phylo_classes import Recommendation, TreeGenerator


class FileUploadView(APIView):
    parser_class = (FileUploadParser)

    def post(self, request, *args, **kwargs):
        file_serializer = DatasetSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# handle pre processing and multiple sequence alignment of raw dataset
class PreprocessView(APIView):
    parser_class = (FileUploadParser)

    def post(self, request, *args, **kwargs):

        file_wrapper = request.FILES['data']
        dp = DataPreprocessor()

        # read and write to a temporary file
        byte_file = io.BytesIO(file_wrapper.file.read())
        temp = "{}.fasta".format(os.path.splitext(request.FILES['data'].name)[0])
        fileHandler = open(temp, "wb")
        fileHandler.write(byte_file.read())
        fileHandler.close()

        # pre process dataset
        output_file = dp.processData(temp)
        print("success preprocess")

        # remove temporary file
        os.remove(temp)

        # multiple sequence alignment
        msa = MuscleMSA()
        out_file = msa.align(output_file)
        print("success align")
        os.remove(output_file)

        try:
            # create a dataset model instance and save to mySQL
            ds = Dataset.objects.create(data=out_file)
            return JsonResponse(dict(doc=ds.id, status=status.HTTP_201_CREATED))
        except:
            return JsonResponse(dict(status=status.HTTP_500_INTERNAL_SERVER_ERROR))


class RecommendView(APIView):

    def get(self, request, *args, **kwargs):
        path = request.GET.get('filepath')
        recommender = Recommendation()
        noOfSeq, lengthOfSeq, typeOfSeq = recommender.readFeaturesFile(path)
        recommendations = recommender.recommendation(noOfSeq, lengthOfSeq, typeOfSeq)
        recommend_serializer = RecommendSerializer(data=recommendations)

        if recommend_serializer.is_valid():
            return Response(recommend_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(recommend_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Generate tree from the user selected algorithm
class TreeGenerationView(APIView):
    def get(self, request, *args, **kwargs):
        data_id = request.GET.get('id')
        algo = request.GET.get('algorithm')

        # Retrieve the dataset record with the request id
        dataset = Dataset.objects.get(pk=data_id)
        generator = TreeGenerator()

        try:
            # run the selected inference algorithm for the dataset
            time = generator.run_algorithm(algo, dataset)
            return JsonResponse(dict(time=time, status=status.HTTP_200_OK))
        except RuntimeError:
            return JsonResponse(dict(status=status.HTTP_400_BAD_REQUEST))
