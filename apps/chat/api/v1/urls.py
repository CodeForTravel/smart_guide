app_name = "chat"

router = DefaultRouter()


urlpatterns = [
    path("", include(router.urls)),
]
