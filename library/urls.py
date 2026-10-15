from rest_framework.routers import DefaultRouter
from .views import BookViewSet, LoanViewSet

router = DefaultRouter(trailing_slash=False)
router.register('books', BookViewSet)
router.register('loans', LoanViewSet)

urlpatterns = router.urls