from rest_framework import serializers

from app.models import Post, Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'photo_50']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'number', 'status', 'author', 'distance', 'sum_distance', 'text', 'date', 'last_update',
                  'edit_reason']
        read_only_fields = ['id', 'date']


class RunnerSerializer(serializers.Serializer):
    profile = ProfileSerializer()
    running_count = serializers.IntegerField()
    distance_sum = serializers.IntegerField()


class StatSerializer(serializers.Serializer):
    start_distance = serializers.IntegerField()
    end_distance = serializers.IntegerField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    all_days_count = serializers.IntegerField()
    interval_days_count = serializers.IntegerField()
    all_distance = serializers.IntegerField()
    max_one_man_distance = RunnerSerializer()
    all_training_count = serializers.IntegerField()
    max_one_man_training_count = RunnerSerializer()

    all_runners_count = serializers.IntegerField()
    interval_runners_count = serializers.IntegerField()
    new_runners = ProfileSerializer(many=True)
    new_runners_count = serializers.IntegerField()
    top_all_runners = RunnerSerializer(many=True)
    top_interval_runners = RunnerSerializer(many=True)

    type = serializers.IntegerField()
    distance_per_day = serializers.FloatField()
    distance_per_training = serializers.FloatField()
    training_count_per_day = serializers.FloatField()
