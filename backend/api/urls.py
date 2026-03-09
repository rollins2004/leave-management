from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    TokenRefreshView,
    EmployeeLeaveListCreateView,
    EmployerLeaveListView,
    EmployerLeaveUpdateView,
)

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Employee
    path('leaves/', EmployeeLeaveListCreateView.as_view(), name='employee-leaves'),

    # Employer
    path('employer/leaves/', EmployerLeaveListView.as_view(), name='employer-leaves'),
    path('employer/leaves/<str:pk>/', EmployerLeaveUpdateView.as_view(), name='employer-leave-update'),
]
