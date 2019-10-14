import csv
import io

from django.http import JsonResponse, FileResponse

import os

from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from phyloGenie.Alignment import MuscleMSA
from phyloGenie.Preprocess import DataPreprocessor
from phyloGenie.ScoreCalculation import SimilarityScoreCalculator
from phyloGenie.models import Dataset
from phyloGenie_backend.settings import MEDIA_ROOT
from .serializers import DatasetSerializer
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

    def post(self, request, *args, **kwargs):
        file_wrapper = request.FILES['data']

        # read and write to a temporary file
        byte_file = io.BytesIO(file_wrapper.file.read())
        temp = "{}.fasta".format(os.path.splitext(request.FILES['data'].name)[0])
        fileHandler = open(temp, "wb")
        fileHandler.write(byte_file.read())
        fileHandler.close()

        # pre process dataset
        dp = DataPreprocessor()
        output_file, data_type = dp.processData(temp)
        print("success preprocess")

        # remove temporary file
        os.remove(temp)

        # multiple sequence alignment
        msa = MuscleMSA()
        alignment, no_of_taxa, seq_len = msa.align(output_file)
        file_name = os.path.splitext(output_file)[0]
        align_file = msa.writeAlignmentFile(alignment, file_name)
        os.remove(output_file)

        sc = SimilarityScoreCalculator()
        result_file = '{}_result.txt'.format(file_name)
        align_file_path = os.path.join(MEDIA_ROOT, align_file)
        score = sc.calculation(align_file_path, data_type, result_file)

        # create a dataset model instance and save to mySQL
        try:
            ds = Dataset.objects.create(data=align_file, size=no_of_taxa, seq_length=seq_len, type=data_type,
                                        sim_score=score)
            return Response(dict(data=ds.id), status=status.HTTP_201_CREATED)
        except RuntimeError:
            return JsonResponse(dict(status=status.HTTP_400_BAD_REQUEST))

        # Call for algorithm recommendation
        # recommender = Recommendation()
        # recommendations = recommender.recommendation(no_of_taxa, seq_len, data_type)
        # recommend_serializer = RecommendSerializer(data=recommendations)
        #
        # if recommend_serializer.is_valid():
        #     return Response(recommend_serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(recommend_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecommendView(APIView):

    def get(self, request, *args, **kwargs):
        # path = request.GET.get('filepath')
        print("recommendation was called")
        data_id = request.GET.get('id')
        dataset = Dataset.objects.get(pk=data_id)
        recommender = Recommendation()
        noOfSeq = dataset.size
        lengthOfSeq = dataset.seq_length
        typeOfSeq = dataset.type
        score = dataset.sim_score
        # noOfSeq, lengthOfSeq, typeOfSeq, score = recommender.readFeaturesFile(path)
        print(noOfSeq, score, typeOfSeq)
        try:
            recommendations = recommender.recommendation(noOfSeq, lengthOfSeq, typeOfSeq, score)
            print(recommendations)
            return Response(dict(algorithms=recommendations, doc_id=data_id), status=status.HTTP_201_CREATED)
        except RuntimeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # recommend_serializer = RecommendSerializer(data=recommendations)

        # if recommend_serializer.is_valid():
        #     return Response(recommend_serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(recommend_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Generate tree from the user selected algorithm
class TreeGenerationView(APIView):
    def get(self, request, *args, **kwargs):
        data_id = request.GET.get('doc_id')
        algo = request.GET.get('algorithm')

        # Retrieve the dataset record with the request id
        dataset = Dataset.objects.get(pk=data_id)
        generator = TreeGenerator()

        try:
            # run the selected inference algorithm for the dataset
            tree = generator.run_algorithm(algo, dataset)
            # file = open(file_path, 'rb')
            # response = FileResponse(file)
            # response['TREE_STRING'] = tree
            # return response
            return Response(dict(tree=tree), status=status.HTTP_201_CREATED)
        except RuntimeError as e:
            return Response(dict(error=e), status=status.HTTP_400_BAD_REQUEST)
