from django.shortcuts import render,redirect
from django.urls import reverse
from django.core.serializers import serialize
from django.template import RequestContext

from rest_framework.views import APIView
from rest_framework import status, permissions, routers, serializers, viewsets,generics
from rest_framework.response import Response

from django.db.models import Q,F,Sum,Value

from .models import TypeDocument,Category,Tags,Hotel,Profile,TypeRoom,ActivityHotel,ActivityRoom, \
City,ActivityRoom,Reservation

from .serializers import NewProfileSerializer,LoginSerializer,NewHotelSerializer,EditHotelSerializer, \
NewRoomSerializer,EdiRoomSerializer, NewActivityHotelSerializer,NewActivityRoomSerializer, \
NewGuestSerializer

from django.contrib.auth.models import Permission, User, Group

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from datetime import datetime, timezone, timedelta
from logs.models import Logs,Actions

# Create your views here.


#index of proyect
class IndexView(APIView):

	def get(self, request):
		if request.user.is_authenticated:
			return render(request, "dashboard.html", {})
		return render(request, "index.html", {})


class LogoutView(APIView):

	def get(self, request):
		logout(request)
		return redirect(reverse('core.login'))


class LoginView(APIView):

	def get(self, request):
		if request.user.is_authenticated:
			return render(request, "dashboard.html", {})
		return render(request, "login.html", {})

	def post(self,request):
		try:
			serializer = LoginSerializer(data=request.data)
			if serializer.is_valid():
				profile = Profile.objects.get(user__username=request.data["email"])
				by_authentic = authenticate(username=request.data["email"], password=request.data["password"])
				if by_authentic is not None:
					user=User.objects.get(username=request.data["email"])
					login(request, user)
					return render(request, "dashboard.html", {})
				else:
					return render(request, "login.html", {'message':"El usuario o la clave no son las correctas"})

			return render(request, "login.html", {'message':"Todos los campos son obligatorios"})

		except ObjectDoesNotExist:
			return render(request, "login.html", {'message':"No existe el usuario"})
		except Exception as e:
			print(e)
			return render(request, "login.html", {'message':"ERROR_SERVER"})


#index of user not administrador, administrador in the admin
class RegisterView(APIView):

	def get(self, request):
		type_document=TypeDocument.objects.filter(type_user=TypeDocument.NATURAL).values("id","name")
		return render(request, "register.html", {"type_document":list(type_document)})

	def post(self,request):
		try:
			serializer = NewProfileSerializer(data=request.data)
			if serializer.is_valid():
				response=serializer.save()
				if response == 0:
					return render(request, "register.html", {'message':"ERROR_SERVER"})

				# return render(request, "login.html", {'message':"Su Registro fue exitoso"})
				user = User.objects.get(pk=response)
				login(request, user)
				return render(request, "dashboard.html", {})

			return render(request, "register.html", {'message':"Todos los campos son obligatorios"})
		except Exception as e:
			return render(request, "register.html", {'message':"ERROR_SERVER"})


#page main
class DashboardView(APIView):

	def get(self, request):
		return render(request, "dashboard.html", {})


#functions hotel register, edit, list, delete
class HotelView(APIView):

	def get(self, request):
		return render(request, "hotel.html", data_hotel(request))


	def post(self,request):
		try:
			serializer = NewHotelSerializer(data=request.data)
			if serializer.is_valid():
				profile=Profile.objects.get(user__id=request.user.id)
				response=serializer.save(owner=profile,user=request.user)
				if response == 0:
					return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)
					# datos=data_hotel(request)
					# datos["message"]="ERROR_SERVER"
					# return render(request, "hotel.html", datos)

				# return render(request, "login.html", {'message':"Su Registro fue exitoso"})
				return Response({'error':False,'message':"OK"}, status=status.HTTP_200_OK)

			return Response({'error':True,'message':"Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			print(e)
			return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)


	def put(self,request):
		try:
			serializer = EditHotelSerializer(data=request.data)
			if serializer.is_valid():
				response=serializer.save(user=request.user)
				if response == 0:
					return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)

				# return render(request, "login.html", {'message':"Su Registro fue exitoso"})
				return Response({'error':False,'message':"OK"}, status=status.HTTP_200_OK)

			return Response({'error':True,'message':"Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)


	def delete(self, request):

		try:
			Hotel.objects.get(pk=request.data["hotel_id"]).delete()

			log_register=Logs(user=request.user,action=Actions.action_delete,name_model='Hotel',id_handle=request.data["hotel_id"])
			log_register.save()
			return Response({'error':False,'message':"OK"}, status=status.HTTP_200_OK)

		except Exception as e:
			return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)

#function retrieve json of hotel
def data_hotel(request):
	type_document=TypeDocument.objects.filter(type_user=TypeDocument.BUSINESS).values("id","name")
	category=Category.objects.all().values("id","name")
	tags=Tags.objects.all().values("id","name")
	city=City.objects.all().values("id","name")
	hoteles=None
	if not request.user.is_superuser:
		profile=Profile.objects.get(user__id=request.user.id)
		hoteles=Hotel.objects.filter(owner=profile).annotate(city_name=(F('city__name'))). \
		values("id","name","date_publish","status","city_name").order_by('-date_created')
	else:
		hoteles=Hotel.objects.all().annotate(city_name=(F('city__name'))). \
		values("id","name","date_publish","status","city_name").order_by('-date_created')

	return {"type_document":list(type_document),
			"category":list(category),"tags":list(tags),"hoteles":list(hoteles),"city":list(city)}



#functions room register, edit, list, delete
class RoomView(APIView):

	def get(self, request):
		return render(request, "rooms.html", data_room(request))

	def post(self,request):
		try:
			serializer = NewRoomSerializer(data=request.data)
			if serializer.is_valid():
				profile=Profile.objects.get(user__id=request.user.id)
				response=serializer.save(owner=profile,user=request.user)
				if response == 0:
					return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)

				# return render(request, "login.html", {'message':"Su Registro fue exitoso"})
				return Response({'error':False,'message':"OK"}, status=status.HTTP_200_OK)

			return Response({'error':True,'message':"Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)


	def put(self,request):
		try:
			serializer = EdiRoomSerializer(data=request.data)
			if serializer.is_valid():
				response=serializer.save(user=request.user)
				if response == 0:
					return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)

				# return render(request, "login.html", {'message':"Su Registro fue exitoso"})
				return Response({'error':False,'message':"OK"}, status=status.HTTP_200_OK)

			return Response({'error':True,'message':"Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)


	def delete(self, request):

		try:
			TypeRoom.objects.get(pk=request.data["room_id"]).delete()
			log_register=Logs(user=request.user,action=Actions.action_delete,name_model='Room',id_handle=request.data["room_id"])
			log_register.save()
			return Response({'error':False,'message':"OK"}, status=status.HTTP_200_OK)

		except Exception as e:
			return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)


def data_room(request):
	hoteles=None
	if not request.user.is_superuser:
		profile=Profile.objects.get(user__id=request.user.id)
		hoteles=Hotel.objects.filter(owner=profile,status=Hotel.ACTIVE).values("id","name","date_publish","status").order_by('-date_created')
	else:
		hoteles=Hotel.objects.filter(status=Hotel.ACTIVE).values("id","name","date_publish","status")

	rooms=None
	if not request.user.is_superuser:
		profile=Profile.objects.get(user__id=request.user.id)
		rooms=TypeRoom.objects.filter(owner=profile,hotel__status=Hotel.ACTIVE).annotate(name_hotel=(F('hotel__name'))). \
		values("id","name","date_publish","status","name_hotel","price","count_person","enable").order_by('-date_created')
	else:
		rooms=TypeRoom.objects.filter(hotel__status=Hotel.ACTIVE).annotate(name_hotel=(F('hotel__name'))). \
		values("id","name","date_publish","status","name_hotel","price","count_person","enable").order_by('-date_created')

	return {"rooms":list(rooms),"hoteles":list(hoteles)}

#retrieve a hotel specific
class RetrieveHotelView(APIView):

	def get(self, request,id):
		info=Hotel.objects.get(pk=id)
		category=""
		tags=""
		list_info=[]
		for item in info.category.all():
			if category == "":
				category=str(item.id)
			else:
				category=category+","+str(item.id)

		for item in info.tags.all():
			if tags == "":
				tags=str(item.id)
			else:
				tags=tags+","+str(item.id)

		list_info.append({
				"id":info.id,
				"name":info.name,
				"category":category,
				"tags":tags,
				"type_document_id":info.type_document.id,
				"number_document":info.number_document,
				"date_publish":info.date_publish,
				"date_inactive":info.date_inactive,
				"city_id":info.city.id,
				"status":info.status
			})
		return JsonResponse({'data':list_info}, status=status.HTTP_200_OK ,safe=False)


#retrieve a room specific
class RetrieveRoomView(APIView):

	def get(self, request,id):
		info=TypeRoom.objects.get(pk=id)
		list_info=[]

		list_info.append({
				"id":info.id,
				"name":info.name,
				"hotel_id":info.hotel.id,
				"price":info.price,
				"count_person":info.count_person,
				"description":info.description,
				"date_publish":info.date_publish,
				"date_inactive":info.date_inactive,
				"status":info.status,
				"enable":info.enable
			})
		return JsonResponse({'data':list_info}, status=status.HTTP_200_OK ,safe=False)



#list all hotel for the reservation
class ReservationView(APIView):

	def get(self, request):
		category_id=request.GET.get('category_id') if request.GET.get('category_id') is not None else 0
		tags_id=request.GET.get('tags_id') if request.GET.get('tags_id') is not None else 0
		city_id=request.GET.get('city_id') if request.GET.get('city_id') is not None else 0
		queryset=(Q(status=Hotel.ACTIVE))

		if int(category_id) > 0:
			queryset= queryset & (Q(category__in=[category_id]))
		if int(tags_id) > 0:
			queryset= queryset & (Q(tags__in=[tags_id]))
		if int(city_id) > 0:
			queryset= queryset & (Q(city_id=city_id))

		query_hoteles=Hotel.objects.filter(queryset).order_by('-date_created')
		hoteles=[]
		category=Category.objects.all().values("id","name")
		tags=Tags.objects.all().values("id","name")
		city=City.objects.all().values("id","name")

		for item in query_hoteles:
			query=[]
			if request.user.id is not None:
				query=ActivityHotel.objects.filter(profile__user=request.user,type_activity=ActivityHotel.LIKE,hotel=item)
			hoteles.append({
				"id":item.id,
				"like":query[0].by_like if len(query) > 0 else False,
				"name":item.name,
				"city":item.city.name
			})

		return render(request, "reservation.html", {"hoteles":hoteles,"categorias":category,"tags":tags,"city":city})


#list all room for the reservation
class RetrieveBookView(APIView):

	def get(self, request,hotel_id):
		date_initial=request.GET.get('date_initial') if request.GET.get('date_initial') is not None else ""
		date_end=request.GET.get('date_end') if request.GET.get('date_end') is not None else ""
		count_person=request.GET.get('count_person') if request.GET.get('count_person') is not None else ""
		
		queryset=(Q(status=TypeRoom.ACTIVE)) & (Q(hotel__id=hotel_id))

		if count_person != "":
			queryset= queryset & (Q(count_person=count_person))

		query_room=TypeRoom.objects.filter(queryset).order_by('-date_created')
		rooms=[]

		for item in query_room:
			query=[]
			if request.user.id is not None:
				query=ActivityRoom.objects.filter(profile__user=request.user,type_activity=ActivityRoom.LIKE,typeroom=item)
			
			sw=0
			if date_initial != "" and date_end != "":
				query_reservation=Reservation.objects.filter(type_room_id=item.id,
					date_initial__range=[date_initial,date_end],date_end__range=[date_initial,date_end])
				review=int(item.enable) - len(query_reservation)
				if review <= 0:
					sw=1 

			if date_initial == "" and date_end != "":
				query_reservation=Reservation.objects.filter(type_room_id=item.id,date_initial=date_end,date_end=date_end)
				review=int(item.enable) - len(query_reservation)
				if review <= 0:
					sw=1 

			if date_initial != "" and date_end == "":
				query_reservation=Reservation.objects.filter(type_room_id=item.id,date_initial=date_initial,date_end=date_initial)
				review=int(item.enable) - len(query_reservation)
				if review <= 0:
					sw=1

			if sw == 0:
				rooms.append({
					"id":item.id,
					"like":query[0].by_like if len(query) > 0 else False,
					"name":item.name,
					"price":item.price,
					"count_person":item.count_person
				})

		return render(request, "book.html", {"rooms":rooms})

#modify the activity of a hotel as like or comment
class ActivityHotelView(APIView):

	def post(self,request):
		try:
			serializer = NewActivityHotelSerializer(data=request.data)
			if serializer.is_valid():
				if request.user.id is not None:
					profile=Profile.objects.get(user__id=request.user.id)
					response=serializer.save(profile=profile,user=request.user)
					if response == 0:
						return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)

					if response == -1:
						return Response({'error':True,'message':"Ya comentaste el hotel"}, status=status.HTTP_400_BAD_REQUEST)

					# return render(request, "login.html", {'message':"Su Registro fue exitoso"})
					return Response({'error':False,'message':"OK"}, status=status.HTTP_200_OK)

				return Response({'error':True,'message':"El usuario debe estar logueando"}, status=status.HTTP_400_BAD_REQUEST)

			return Response({'error':True,'message':"Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)


#list the comments of a hotel specific
class CommentView(APIView):

	def get(self, request,id_hotel):
		hotel=Hotel.objects.get(pk=id_hotel)
		comments=ActivityHotel.objects.filter(hotel_id=id_hotel,type_activity=ActivityHotel.COMMENT).annotate(username=(F('profile__user__username'))). \
		values("id","comment","date_created","username").order_by('-date_created')

		return render(request, "comment_hotel.html", {"comments":comments,"hotel":hotel})


#modify or create the activity of a room as like or comment
class ActivityRoomView(APIView):

	def post(self,request):
		try:
			serializer = NewActivityRoomSerializer(data=request.data)
			if serializer.is_valid():
				if request.user.id is not None:
					profile=Profile.objects.get(user__id=request.user.id)
					response=serializer.save(profile=profile,user=request.user)
					if response == 0:
						return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)

					if response == -1:
						return Response({'error':True,'message':"Ya comentaste la habitacion"}, status=status.HTTP_400_BAD_REQUEST)

					# return render(request, "login.html", {'message':"Su Registro fue exitoso"})
					return Response({'error':False,'message':"OK"}, status=status.HTTP_200_OK)

				return Response({'error':True,'message':"El usuario debe estar logueando"}, status=status.HTTP_400_BAD_REQUEST)

			print(serializer.errors)
			return Response({'error':True,'message':"Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)


#list the comments of a room
class CommentRoomView(APIView):

	def get(self, request,id_room):
		room=TypeRoom.objects.get(pk=id_room)
		comments=ActivityRoom.objects.filter(typeroom_id=id_room,type_activity=ActivityRoom.COMMENT).annotate(username=(F('profile__user__username'))). \
		values("id","comment","date_created","username").order_by('-date_created')

		return render(request, "comment_room.html", {"comments":comments,"room":room})


#page when guest is register
class PageGuestView(APIView):

	def get(self, request,id_room):
		room=TypeRoom.objects.get(pk=id_room)
		type_document=TypeDocument.objects.filter(type_user=TypeDocument.NATURAL).values("id","name")
		return render(request, "guest.html", {"room":room,"type_document":type_document})


#save the reservation
class GuestView(APIView):

	def post(self,request):
		try:
			serializer = NewGuestSerializer(data=request.data)
			if serializer.is_valid():
				if request.user.id is not None:
					profile=Profile.objects.get(user__id=request.user.id)
					response=serializer.save(profile=profile,user=request.user)
					if response == 0:
						return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)

					if response == -1:
						return Response({'error':True,'message':"La fecha no esta disponible"}, status=status.HTTP_400_BAD_REQUEST)

					# return render(request, "login.html", {'message':"Su Registro fue exitoso"})
					return Response({'error':False,'message':response}, status=status.HTTP_200_OK)

				return Response({'error':True,'message':"El usuario debe estar logueando"}, status=status.HTTP_400_BAD_REQUEST)

			print(serializer.errors)
			return Response({'error':True,'message':"Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'error':True,'message':"ERROR_SERVER"}, status=status.HTTP_400_BAD_REQUEST)

#page when yo can show the detail of the reservation
class DetailReservationView(APIView):

	def get(self, request,reservation_id):
		query_reservation=Reservation.objects.get(pk=reservation_id)

		a = query_reservation.date_initial
		b = query_reservation.date_end
		delta = b - a
		total=int(delta.days)*query_reservation.type_room.price
		reservation=[]
		reservation.append({
			"name_hotel":query_reservation.type_room.hotel.name,
			"name_room":query_reservation.type_room.name,
			"name_city":query_reservation.type_room.hotel.city.name,
			"total":total,
			"count_person":query_reservation.type_room.count_person,
			"price":query_reservation.type_room.price,
			"description":query_reservation.description,
			"date_initial":query_reservation.date_initial,
			"date_end":query_reservation.date_end
		})

		return render(request, "detail_reservation.html", {"reservation":reservation[0]})


#for method get list all the reservation
class ListReservationView(APIView):

	def get(self, request):

		query_reservation=None
		if not request.user.is_superuser:
			profile=Profile.objects.get(user__id=request.user.id)
			query_reservation=Reservation.objects.filter(type_room__hotel__owner=profile).order_by("-date_created")
		else:
			query_reservation=Reservation.objects.all().order_by("-date_created")

		query_reservation=Reservation.objects.all().order_by("-date_created")
		list_reservation=[]

		for item in query_reservation:
			a = item.date_initial
			b = item.date_end
			delta = b - a
			total=int(delta.days)*item.type_room.price
			list_reservation.append({
					"id":item.id,
					"full_name":item.guest.full_name,
					"name_hotel":item.type_room.hotel.name,
					"name_room":item.type_room.name,
					"total":total,
					"count_person":item.type_room.count_person
				})


		return render(request, "list_reservation.html", {"list_reservation":list_reservation})