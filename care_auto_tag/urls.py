from rest_framework.routers import DefaultRouter

from care_auto_tag.api.viewsets.health_check import HealthCheckViewSet

router = DefaultRouter()

router.register("health_check", HealthCheckViewSet, basename="auto_tag__health_check")

urlpatterns = router.urls
