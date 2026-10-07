from django.urls import path


from meethub.profile import views


app_name = 'profile'
urlpatterns = [
    path('edit/', views.edit_profile, name='edit'),
    path('detail/<int:pk>/', views.UserDetail.as_view(), name='detail'),
    path('detail/<int:pk>/map/', views.UserDetailMap.as_view(), name='detail-map'),
]
