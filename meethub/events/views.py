from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from meethub.actions.utils import create_action
from meethub.comments.models import Comment
from meethub.comments.forms import CommentForm

from meethub.events.models import Event
from meethub.events.forms import EventForm


# Create your views here.


class EventList(LoginRequiredMixin, generic.ListView):
    model = Event
    template_name = 'events/list_of_events.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        queryset = Event.objects.all()
        
        sort_by = self.request.GET.get('sort', 'date')
        order = self.request.GET.get('order')
        
        # Set default order based on sort type
        if order is None:
            if sort_by == 'attendees':
                order = 'desc'  # Biggest to least
            else:
                order = 'asc'  # Soonest, alphabetical, closest
        
        if sort_by == 'date':
            queryset = queryset.order_by('date', 'time')
        elif sort_by == 'category':
            queryset = queryset.order_by('category__name')
        elif sort_by == 'attendees':
            queryset = queryset.annotate(
                attendee_count=Count('attendees')
            ).order_by('attendee_count')
        
        if order == 'desc':
            queryset = queryset.reverse()
        
        return queryset


class MapEventList(LoginRequiredMixin, generic.ListView):
    model = Event
    template_name = 'events/map_events.html'
    context_object_name = 'events'
    paginate_by = 20

    def get_queryset(self):
        queryset = Event.objects.all()
        
        sort_by = self.request.GET.get('sort', 'date')
        order = self.request.GET.get('order')
        
        # Set default order based on sort type
        if order is None:
            if sort_by == 'attendees':
                order = 'desc'  # Biggest to least
            else:
                order = 'asc'  # Soonest, alphabetical, closest
        
        if sort_by == 'date':
            queryset = queryset.order_by('date', 'time')
        elif sort_by == 'category':
            queryset = queryset.order_by('category__name')
        elif sort_by == 'attendees':
            queryset = queryset.annotate(
                attendee_count=Count('attendees')
            ).order_by('attendee_count')
        
        if order == 'desc':
            queryset = queryset.reverse()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get first event with coordinates for map centering
        first_event = self.get_queryset().filter(latitude__isnull=False, longitude__isnull=False).first()
        if first_event:
            context['first_event_lat'] = first_event.latitude
            context['first_event_lon'] = first_event.longitude
        return context


class EventDisplay(generic.DetailView):
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.all()
        context['attending'] = self.get_object().attendees.all
        return context


class EventDisplayMap(generic.DetailView):
    model = Event
    template_name = 'events/detail_map.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.all()
        context['attending'] = self.get_object().attendees.all
        return context


class CommentCreate(SuccessMessageMixin, generic.CreateView):
    model = Comment
    template_name = 'events/detail.html'
    fields = ('comment',)
    success_message = 'Comment was added successfully'

    def form_valid(self, form):
        form.instance = form.save(commit=False)
        form.instance.event = self.get_object(queryset=Event.objects.all())
        form.instance.created_by = self.request.user
        # create_action(self.request.user, 'added a comment', form.instance)
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('events:event-detail', kwargs={'pk': self.get_object(Event.objects.all()).pk})


class CommentCreateMap(SuccessMessageMixin, generic.CreateView):
    model = Comment
    template_name = 'events/detail_map.html'
    fields = ('comment',)
    success_message = 'Comment was added successfully'

    def form_valid(self, form):
        form.instance = form.save(commit=False)
        form.instance.event = self.get_object(queryset=Event.objects.all())
        form.instance.created_by = self.request.user
        # create_action(self.request.user, 'added a comment', form.instance)
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('events:event-detail-map', kwargs={'pk': self.get_object(Event.objects.all()).pk})


class EventDetail(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        view = EventDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentCreate.as_view()
        return view(request, *args, **kwargs)


class EventDetailMap(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        view = EventDisplayMap.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentCreateMap.as_view()
        return view(request, *args, **kwargs)


class EventFormMixin(object):
    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        create_action(self.request.user, 'created a new event', form.instance)
        return response


class EventCreate(LoginRequiredMixin, SuccessMessageMixin, EventFormMixin, generic.CreateView):
    model = Event
    template_name = 'events/create_form.html'
    form_class = EventForm
    # fields = ('category', 'name', 'details', 'venue', 'time', 'date')
    context_object_name = 'event'
    success_message = "%(name)s was created successfully"

    def get_success_url(self):
        return reverse_lazy('events:event-detail', kwargs={'pk': self.object.pk})


class EventCreateMap(LoginRequiredMixin, SuccessMessageMixin, EventFormMixin, generic.CreateView):
    model = Event
    template_name = 'events/create_event_map.html'
    form_class = EventForm
    context_object_name = 'event'
    success_message = "%(name)s was created successfully"

    def get_success_url(self):
        return reverse_lazy('events:event-detail', kwargs={'pk': self.object.pk})

    
class EventUpdate(LoginRequiredMixin, SuccessMessageMixin, EventFormMixin, generic.UpdateView):
    model = Event
    template_name = 'events/update_form.html'
    template_name_suffix = '_update_form'
    fields = ('category', 'name', 'details', 'venue', 'time', 'date', 'latitude', 'longitude', 'is_private_location',)
    success_message = "%(name)s was updated successfully"

    def get_success_url(self):
        return reverse_lazy('events:event-detail', kwargs={'pk': self.object.pk})


class EventDelete(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Event
    template_name = 'events/delete.html'
    success_url = reverse_lazy('events:event-list')
    context_object_name = 'event'
    success_message = "Event was deleted successfully"


class EventUpdateMap(LoginRequiredMixin, SuccessMessageMixin, EventFormMixin, generic.UpdateView):
    model = Event
    template_name = 'events/update_event_map.html'
    template_name_suffix = '_update_form'
    fields = ('category', 'name', 'details', 'venue', 'time', 'date', 'latitude', 'longitude', 'is_private_location',)
    success_message = "%(name)s was updated successfully"

    def get_success_url(self):
        return reverse_lazy('events:event-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object
        return context


class EventDeleteMap(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Event
    template_name = 'events/delete_event_map.html'
    success_url = reverse_lazy('events:event-list')
    context_object_name = 'event'
    success_message = "Event was deleted successfully"


@login_required()
def attend_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event.attendees.add(request.user)
    create_action(request.user, 'is attending', event)
    messages.success(request, 'You are now attending {0}'.format(event.name))
    
    return redirect('events:event-detail', pk=event.pk)


@login_required()
def not_attend_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event.attendees.remove(request.user)
    create_action(request.user, 'no longer attending', event)
    messages.success(request, 'You are no longer attending {0}'.format(event.name))
    
    return redirect('events:event-detail', pk=event.pk)

