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
