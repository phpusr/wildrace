from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.forms import StatForm, PostForm
from app.models import Post, Config
from app.permissions import IsAdminUserOrReadOnly
from app.serializers import PostSerializer, StatSerializer, ConfigSerializer
from app.services import stat_service, index_page_service, sync_service
from ws import ws_service
from ws.ws_service import ObjectType, EventType


def index(request):
    data = index_page_service.get_data(request.user)
    return render(request, 'app/index.html', data)


class PostViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = [IsAdminUserOrReadOnly]
    serializer_class = PostSerializer

    @action(detail=False, methods=['put'])
    def sync(self, request):
        sync_service.sync_posts()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    def perform_update(self, serializer: PostSerializer):
        super().perform_update(serializer)
        ws_service.main_group_send(serializer.data, ObjectType.POST, EventType.UPDATE)
        self._update_data(self.get_object())

    def perform_destroy(self, instance: Post):
        object_id = instance.id
        super().perform_destroy(instance)
        ws_service.main_group_send(object_id, ObjectType.POST, EventType.REMOVE)
        instance.number = None
        self._update_data(instance)

    def _update_next_posts(self):
        return self.request.query_params.get('update_next_posts') == 'true'

    def _update_data(self, post: Post):
        if self._update_next_posts():
            sync_service.update_next_posts(post)

        stat_service.update_stat()


class StatViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAdminUserOrReadOnly]
    serializer_class = StatSerializer

    def list(self, request):
        form = StatForm(request.query_params)
        if form.is_valid():
            stat = stat_service.calc_stat(
                stat_type=form.stat_type,
                start_range=form.cleaned_data['start_range'],
                end_range=form.cleaned_data['end_range']
            )
            serializer = self.get_serializer(stat)
            return Response(serializer.data)
        else:
            return Response(form.errors)

    @action(detail=False, methods=['post'])
    def publish(self, request):
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


class ConfigViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    queryset = Config.objects.filter(id=1)
    serializer_class = ConfigSerializer
