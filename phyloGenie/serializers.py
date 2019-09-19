from rest_framework import serializers
from phyloGenie.models import Dataset
from phyloGenie.models import Recommendations


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ('data', 'size', 'seq_length', 'type', 'sim_score')


class RecommendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendations
        fields = "__all__"
