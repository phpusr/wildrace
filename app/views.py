from django.conf import settings
from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from app.forms import StatForm
from app.models import TempData, Post, Config
from app.serializers import PostSerializer, StatSerializer, ConfigSerializer
from app.services import stat_service, vk_api_service


def index(request):
    host = 'http://192.168.1.100:8080/' if settings.DEBUG else '/'

    user = request.user
    result = {
        'google_analytics_id': '',
        'js_files': [
            f'{host}js/app.js',
            f'{host}js/chunk-vendors.js'
        ],
        'css_files': [],
        'frontend_data': {
            'user': {
                'username': user.username,
                'isSuperuser': request.user.is_superuser
            } if user.is_authenticated else None,
            'stat': stat_service.get_stat(),
            'lastSyncDate': TempData.objects.get().last_sync_date.timestamp(),
            'config': {
                'projectVersion': settings.VERSION,
                'groupLink': vk_api_service.get_group_url()
            }
        }
    }
    return render(request, 'app/index.html', result)


class PostViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = Post.objects.order_by('-date')

        manual_editing = self.request.query_params.get('me')
        if manual_editing:
            queryset = queryset.filter(last_update__isnull=False)

        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class ConfigViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer


class StatView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        form = StatForm(request.GET)
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


class StatPublishView(APIView):
    def post(self, request, format=None):
        form = StatForm(request.POST)
        if form.is_valid():
            stat = stat_service.calc_stat(
                stat_type=form.stat_type,
                start_range=form.cleaned_data['start_range'],
                end_range=form.cleaned_data['end_range']
            )
            post_id = stat_service.publish_stat_post(stat)
            return Response(post_id)
        return Response(form.errors)
