from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from app.forms import StatForm, PostForm
from app.models import Post, Config
from app.permissions import IsAdminUserOrReadOnly
from app.serializers import PostSerializer, StatSerializer, ConfigSerializer
from app.services import stat_service, index_page_service


def index(request):
    data = index_page_service.get_data(request.user)
    return render(request, 'app/index.html', data)


class PostViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = [IsAdminUserOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        form = PostForm(self.request.query_params)
        if not form.is_valid():
            return Post.objects.none()

        queryset = Post.objects.order_by('-date')

        manual_editing = form.cleaned_data['me']
        if manual_editing == 'true':
            queryset = queryset.filter(last_update__isnull=False)

        status = form.cleaned_data['status']
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class StatView(APIView):
    permission_classes = [IsAdminUserOrReadOnly]

    def get(self, request, format=None):
        form = StatForm(request.query_params)
        if form.is_valid():
            stat = stat_service.calc_stat(
                stat_type=form.stat_type,
                start_range=form.cleaned_data['start_range'],
                end_range=form.cleaned_data['end_range']
            )
            serializer = StatSerializer(stat)
            return Response(serializer.data)
        else:
            return Response(form.errors)

    def post(self, request, format=None):
        form = StatForm(request.data)
        if form.is_valid():
            stat = stat_service.calc_stat(
                stat_type=form.stat_type,
                start_range=form.cleaned_data['start_range'],
                end_range=form.cleaned_data['end_range']
            )
            post_id = stat_service.publish_stat_post(stat)
            return Response(post_id)
        return Response(form.errors)


class ConfigViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
