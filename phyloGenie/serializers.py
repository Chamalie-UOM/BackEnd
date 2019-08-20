from rest_framework import serializers
from phyloGenie.models import Dataset, PreprocessModel
from phyloGenie.models import Recommendations

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = "__all__"

class RecommendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendations
        fields = "__all__"

class PreprocessSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreprocessModel
        fields = ('data_clean_time', 'alignment_time')