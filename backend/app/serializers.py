from rest_framework import serializers

from app.models import Post, Profile, Config, User
from app.services import vk_api_service


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff', 'is_authenticated']


class SimpleStatSerializer(serializers.Serializer):
    distance_sum = serializers.IntegerField()
    running_count = serializers.IntegerField()
    post_count = serializers.IntegerField()


class SimpleConfigSerializer(serializers.Serializer):
    project_version = serializers.CharField()
    group_link = serializers.CharField()


class FrontendDataSerializer(serializers.Serializer):
    user = UserSerializer()
    stat = SimpleStatSerializer()
    last_sync_date = serializers.IntegerField()
    config = SimpleConfigSerializer()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'photo_50']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'vk_id', 'number', 'status', 'author', 'distance', 'sum_distance', 'text', 'date',
                  'last_update', 'edit_reason']
        read_only_fields = ['id', 'vk_id', 'date']


class ConfigSerializer(serializers.ModelSerializer):
    authorize_url = serializers.SerializerMethodField()

    class Meta:
        model = Config
        fields = '__all__'
        read_only_fields = ['id']

    def get_authorize_url(self, instance):
        return vk_api_service.get_authorize_url()


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
