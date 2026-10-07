from django.urls import path
from meethub.events import views

app_name = 'events'
urlpatterns = [
    path('', views.MapEventList.as_view(), name='event-list'),
    path('events/list/', views.EventList.as_view(), name='event-list-view'),
    path('<int:pk>/', views.EventDetailMap.as_view(), name='event-detail'),
    path('new/', views.EventCreateMap.as_view(), name='event-create' ),
    path('<int:pk>/delete/', views.EventDeleteMap.as_view(), name='event-delete'),
    path('<int:pk>/update/', views.EventUpdateMap.as_view(), name='event-update'),
    path('<event_id>/attend/', views.attend_event, name='attend_event'),
    path('<event_id>/not_attend/', views.not_attend_event, name='not_attend_event'),

]
