
from django.conf.urls import url 
from . import views
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [

    # url(r'^', views.index, name='core.index'),
    url(r'^$', views.IndexView.as_view(),name="core.index"),
    url(r'^login/$', views.LoginView.as_view(),name="core.login"),
    url(r'^register/$', views.RegisterView.as_view(),name="core.register"),
    url(r'^dashboard/$', views.DashboardView.as_view(),name="core.dashboard"),
    url(r'^logout/$', views.LogoutView.as_view(),name="core.logout"),
    url(r'^hotel/$', views.HotelView.as_view(),name="core.hotel"),
    url(r'^rooms/$', views.RoomView.as_view(),name="core.rooms"),
    url(r'^reservation/$', views.ReservationView.as_view(),name="core.reservation"),
    url(r'^hotel/(?P<id>[0-9]+)/$', views.RetrieveHotelView.as_view(),name="core.hotel"),
    url(r'^rooms/(?P<id>[0-9]+)/$', views.RetrieveRoomView.as_view(),name="core.rooms"),
    url(r'^book/(?P<hotel_id>[0-9]+)/$', views.RetrieveBookView.as_view(),name="core.rooms"),
    url(r'^activity_hotel/$', views.ActivityHotelView.as_view(),name="core.activity_hotel"),
    url(r'^comment_hotel/(?P<id_hotel>[0-9]+)/$', views.CommentView.as_view(),name="core.coment_hotel"),
    url(r'^coment_room/(?P<id_room>[0-9]+)/$', views.CommentRoomView.as_view(),name="core.coment_room"),
    url(r'^activity_room/$', views.ActivityRoomView.as_view(),name="core.activity_room"),
    url(r'^guest/(?P<id_room>[0-9]+)/$', views.PageGuestView.as_view(),name="core.page_guest"),
    url(r'^guest/$', views.GuestView.as_view(),name="core.guest"),
    url(r'^detail_reservation/(?P<reservation_id>[0-9]+)/$', views.DetailReservationView.as_view(),name="core.detail_reservation"),
    url(r'^list_reservation/$', views.ListReservationView.as_view(),name="core.list_reservation"),

]

