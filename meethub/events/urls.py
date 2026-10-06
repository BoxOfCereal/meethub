from django.urls import path
from meethub.events import views

app_name = 'events'
urlpatterns = [
    path('events/', views.EventList.as_view(), name='event-list'),
    path('events/map/', views.MapEventList.as_view(), name='event-map'),
    path('events/<int:pk>/', views.EventDetail.as_view(), name='event-detail'),
    path('events/map/<int:pk>/', views.EventDetailMap.as_view(), name='event-detail-map'),
    path('events/new/', views.EventCreate.as_view(), name='event-create' ),
    path('events/map/new/', views.EventCreateMap.as_view(), name='event-create-map' ),
    path('events/<int:pk>/delete', views.EventDelete.as_view(), name='event-delete'),
    path('events/<int:pk>/update', views.EventUpdate.as_view(), name='event-update'),
    path('events/<event_id>/attend/', views.attend_event, name='attend_event'),
    path('events/<event_id>/not_attend/', views.not_attend_event, name='not_attend_event'),

]
