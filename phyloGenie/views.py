import csv
import io
import time
import json
from typing import TextIO

from django.core.files import File
from django.shortcuts import render

# Create your views here.
import os
from django.conf import settings
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from phyloGenie.Alignment import MuscleMSA
from phyloGenie.Preprocess import DataPreprocessor
from .serializers import FileSerializer, PreprocessSerializer
from .serializers import RecommendSerializer
from .phylo_classes import Recommendation


class FileUploadView(APIView):
    parser_class = (FileUploadParser)

    def post(self, request, *args, **kwargs):
      file_serializer = FileSerializer(data=request.data)

      if file_serializer.is_valid():
          file_serializer.save()
          return Response(file_serializer.data, status=status.HTTP_201_CREATED)
      else:
          return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecommendView(APIView):
    
    def get(self, request, *args, **kwargs):
        path = request.GET.get('filepath')
        recommender = Recommendation()
        noOfSeq, lengthOfSeq, typeOfSeq = recommender.readFeaturesFile(path)
        recommendations = recommender.recommendation(noOfSeq, lengthOfSeq, typeOfSeq)
        recommend_serializer=RecommendSerializer(data=recommendations)

        if recommend_serializer.is_valid():
            return Response(recommend_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(recommend_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PreprocessView(APIView):
    parser_class = (FileUploadParser)

    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data)
      #
        # if file_serializer.is_valid():
        #    file_serializer.save()
      # body_unicode = request.body.decode('utf-8')
      # body = json.loads(body_unicode)
        file_wrapper=request.FILES['data']
        dp = DataPreprocessor()
        clean_start = time.time()
        #print(type(file_wrapper.file.read()))
        b = io.BytesIO(file_wrapper.file.read())
        temp="file.fasta"
        out=open(temp,"wb")
        out.write(b.read())
     
        out.close()

        output_file = dp.processData(temp)
        clean_end = time.time()
        os.remove(temp)
        align_start = time.time()
        msa = MuscleMSA()
        align_end = time.time()
        out_file = msa.align(output_file)

        outFile_serializer=FileSerializer(data=out_file)
        if outFile_serializer.is_valid():
            outFile_serializer.save()
        clean_time = clean_end-clean_start
        align_time = align_end-align_start
        print(clean_time)
        print(align_time)
        preprocess_serializer = PreprocessSerializer(data={'data_clean_time':clean_time,'alignment_time':align_time})

        if preprocess_serializer.is_valid():
            return Response(preprocess_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(preprocess_serializer.errors, status=status.HTTP_400_BAD_REQUEST)