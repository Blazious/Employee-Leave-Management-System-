from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeaveTypeViewSet, 
    LeaveRequestViewSet, 
    LeaveBalanceViewSet,
    test_holiday_calculation
)

router = DefaultRouter()
router.register(r"leave-types", LeaveTypeViewSet, basename="leave-types")
router.register(r"leave-requests", LeaveRequestViewSet, basename="leave-requests")
router.register(r"leave-balances", LeaveBalanceViewSet, basename="leave-balances")

urlpatterns = [
    path("", include(router.urls)),
    path("test-holidays/", test_holiday_calculation, name="test-holidays"),
]
