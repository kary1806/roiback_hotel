from django.shortcuts import render
from .models import Profile,Hotel,TypeRoom,ActivityHotel,ActivityRoom,Guest,Reservation
from rest_framework import status, permissions, routers, serializers, viewsets
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction, connection

from django.contrib.auth.models import Permission, User, Group
from datetime import datetime, timezone, timedelta
from django.conf import settings
from logs.models import Logs,Actions

class NewProfileSerializer(serializers.Serializer):

	email = serializers.CharField(required=True, max_length=250)
	first_name = serializers.CharField(required=True, max_length=250)
	last_name = serializers.CharField(required=True, max_length=250)
	gender = serializers.CharField(required=True, max_length=250)
	date_birth = serializers.CharField(required=True, max_length=250)
	type_document_id = serializers.CharField(required=True, max_length=250)
	number_document = serializers.CharField(required=True, max_length=250)
	phone = serializers.CharField(required=True, max_length=250)
	password = serializers.CharField(required=True, max_length=250)

	def create(self, data):
		"""
		this serializers handles registration creates a User, Profile
		"""
		try:
			newUser = User.objects.create_user(username=data.get("email"),
			first_name=data.get("first_name"),
			last_name=data.get("last_name"),
			email=data.get("email"))

			user_model=User.objects.get(pk=newUser.id)
			user_model.set_password(data.get('password'))
			user_model.save()

			log_register=Logs(user=newUser,action=Actions.action_create,name_model='User',id_handle=newUser.id)
			log_register.save()

			newProfile=Profile(user_id=newUser.id,
					phone=data.get("phone"),
					date_birth=data.get("date_birth"),
					gender=data.get("gender"),
					type_document_id=data.get("type_document_id"),
					number_document=data.get("number_document")
			)

			newProfile.save()

			log_register=Logs(user=newUser,action=Actions.action_create,name_model='Profile',id_handle=newProfile.id)
			log_register.save()

			return newProfile.id

		except Exception as e:
			print(e)
			return 0


class LoginSerializer(serializers.Serializer):

	email = serializers.CharField(required=True, max_length=250)
	password = serializers.CharField(required=True, max_length=250)



class NewHotelSerializer(serializers.Serializer):

	name = serializers.CharField(required=True, max_length=250)
	type_document_id = serializers.CharField(required=True, max_length=250)
	city_id = serializers.CharField(required=True, max_length=250)
	status = serializers.CharField(required=True, max_length=250)
	number_document = serializers.CharField(required=True, max_length=250)
	category = serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	tags = serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	date_publish=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	date_inactive=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)

	def create(self, data):
		"""
		this serializers handles registration new Hotel
		"""
		try:
			status=data.get("status")
			date_now= datetime.now().strftime('%Y-%m-%d')
			if data.get("date_publish")!="":
				if date_now != data.get("date_publish"):
					status=Hotel.INACTIVE

			newHotel=Hotel(
					name=data.get("name"),
					type_document_id=data.get("type_document_id"),
					number_document=data.get("number_document"),
					city_id=data.get("city_id"),
					owner=data.get("owner"),
					date_publish=data.get("date_publish") if data.get("date_publish") != "" else None,
					date_inactive=data.get("date_inactive") if data.get("date_inactive") != "" else None,
					status=status
				)
			newHotel.save()

			if data.get("category") != "":
				category=data.get("category").split(",")
				newHotel.category.add(*category)
				newHotel.save()

			if data.get("tags") != "":
				tags=data.get("tags").split(",")
				newHotel.tags.add(*tags)
				newHotel.save()

			log_register=Logs(user=data.get("user"),action=Actions.action_create,name_model='Hotel',id_handle=newHotel.id)
			log_register.save()

			return newHotel.id

		except Exception as e:
			print(e)
			return 0


class EditHotelSerializer(serializers.Serializer):

	id = serializers.CharField(required=True, max_length=250)
	name = serializers.CharField(required=True, max_length=250)
	status = serializers.CharField(required=True, max_length=250)
	type_document_id = serializers.CharField(required=True, max_length=250)
	city_id = serializers.CharField(required=True, max_length=250)
	number_document = serializers.CharField(required=True, max_length=250)
	category = serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	tags = serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	date_publish=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	date_inactive=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)

	def create(self, data):
		"""
		this serializers handles  edit a Hotel
		"""
		try:
			status=data.get("status")
			date_now= datetime.now().strftime('%Y-%m-%d')
			if data.get("date_publish")!="":
				if date_now != data.get("date_publish"):
					status=Hotel.INACTIVE

			update_hotel=Hotel.objects.get(pk=data.get("id"))
			update_hotel.name=data.get("name")
			update_hotel.city_id=data.get("city_id")
			update_hotel.type_document_id=data.get("type_document_id")
			update_hotel.number_document=data.get("number_document")
			update_hotel.date_publish=data.get("date_publish") if data.get("date_publish") != "" else None
			update_hotel.date_inactive=data.get("date_inactive") if data.get("date_inactive") != "" else None
			update_hotel.status=status
			update_hotel.category.clear()
			update_hotel.tags.clear()
			update_hotel.save()

			if data.get("category") != "":
				category=data.get("category").split(",")
				print(category)
				update_hotel.category.add(*category)
				update_hotel.save()

			if data.get("tags") != "":
				tags=data.get("tags").split(",")
				print(tags)
				update_hotel.tags.add(*tags)
				update_hotel.save()

			log_register=Logs(user=data.get("user"),action=Actions.action_update,name_model='Hotel',id_handle=update_hotel.id)
			log_register.save()

			return update_hotel.id

		except Exception as e:
			print(e)
			return 0


class NewRoomSerializer(serializers.Serializer):

	name = serializers.CharField(required=True, max_length=250)
	hotel_id = serializers.CharField(required=True, max_length=250)
	price = serializers.CharField(required=True, max_length=250)
	status = serializers.CharField(required=True, max_length=250)
	enable = serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	count_person = serializers.CharField(required=True, max_length=250,allow_blank=True)
	description = serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	date_publish=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	date_inactive=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)

	def create(self, data):
		"""
		this serializers handles registration creates a Room
		"""
		try:
			status=data.get("status")
			date_now= datetime.now().strftime('%Y-%m-%d')
			if data.get("date_publish")!="":
				if date_now != data.get("date_publish"):
					status=TypeRoom.INACTIVE

			newRoom=TypeRoom(
					name=data.get("name"),
					hotel_id=data.get("hotel_id"),
					enable=data.get("enable"),
					price=data.get("price"),
					count_person=data.get("count_person"),
					description=data.get("description"),
					owner=data.get("owner"),
					date_publish=data.get("date_publish") if data.get("date_publish") != "" else None,
					date_inactive=data.get("date_inactive") if data.get("date_inactive") != "" else None,
					status=status
				)
			newRoom.save()

			log_register=Logs(user=data.get("user"),action=Actions.action_create,name_model='Room',id_handle=newRoom.id)
			log_register.save()

			return newRoom.id

		except Exception as e:
			print(e)
			return 0



class EdiRoomSerializer(serializers.Serializer):

	id = serializers.CharField(required=True, max_length=250)
	name = serializers.CharField(required=True, max_length=250)
	hotel_id = serializers.CharField(required=True, max_length=250)
	price = serializers.CharField(required=True, max_length=250)
	status = serializers.CharField(required=True, max_length=250)
	enable = serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	count_person = serializers.CharField(required=True, max_length=250,allow_blank=True)
	description = serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	date_publish=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)
	date_inactive=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)

	def create(self, data):
		"""
		this serializers handles redit room
		"""
		try:
			status=data.get("status")
			date_now= datetime.now().strftime('%Y-%m-%d')
			if data.get("date_publish")!="":
				if date_now != data.get("date_publish"):
					status=TypeRoom.INACTIVE

			update_room=TypeRoom.objects.get(pk=data.get("id"))
			update_room.name=data.get("name")
			update_room.hotel_id=data.get("hotel_id")
			update_room.price=data.get("price")
			update_room.enable=data.get("enable")
			update_room.count_person=data.get("count_person")
			update_room.date_publish=data.get("date_publish") if data.get("date_publish") != "" else None
			update_room.date_inactive=data.get("date_inactive") if data.get("date_inactive") != "" else None
			update_room.status=status
			update_room.save()
			
			return update_room.id

			log_register=Logs(user=data.get("user"),action=Actions.action_update,name_model='Room',id_handle=update_room.id)
			log_register.save()

		except Exception as e:
			print(e)
			return 0


class NewActivityHotelSerializer(serializers.Serializer):

	hotel_id = serializers.CharField(required=True, max_length=250)
	type_activity = serializers.CharField(required=True, max_length=250)
	by_like=serializers.BooleanField(required=True)
	comment=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)

	def create(self, data):
		"""
		this serializers handles activity hotel
		"""
		try:
			newActivity=None
			if ActivityHotel.LIKE == int(data.get("type_activity")):
				query_activity=ActivityHotel.objects.filter(profile=data.get("profile"),hotel_id=data.get("hotel_id"),type_activity=data.get("type_activity"))
				if len(query_activity) == 0:
					newActivity=ActivityHotel(
							hotel_id=data.get("hotel_id"),
							by_like=data.get("by_like"),
							profile=data.get("profile"),
							type_activity=data.get("type_activity")
						)

				else:
					update_activity=ActivityHotel.objects.get(pk=query_activity[0].id)
					update_activity.by_like=data.get("by_like")
					update_activity.save()
					log_register=Logs(user=data.get("user"),action=Actions.action_update,name_model='ActivityHotel',id_handle=update_activity.id)
					log_register.save()
					return update_activity.id


			elif ActivityHotel.COMMENT == int(data.get("type_activity")):
				query_activity=ActivityHotel.objects.filter(profile=data.get("profile"),hotel_id=data.get("hotel_id"),type_activity=data.get("type_activity"))
				if len(query_activity) == 0:
					newActivity=ActivityHotel(
							hotel_id=data.get("hotel_id"),
							comment=data.get("comment"),
							profile=data.get("profile"),
							type_activity=data.get("type_activity")
						)
				else:
					return -1

			if newActivity is not None:
				newActivity.save()
				log_register=Logs(user=data.get("user"),action=Actions.action_create,name_model='ActivityHotel',id_handle=newActivity.id)
				log_register.save()
				return newActivity.id
			
			return 1

		except Exception as e:
			print(e)
			return 0


class NewActivityRoomSerializer(serializers.Serializer):

	typeroom_id = serializers.CharField(required=True, max_length=250)
	type_activity = serializers.CharField(required=True, max_length=250)
	by_like=serializers.BooleanField(required=True)
	comment=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)

	def create(self, data):
		"""
		this serializers handles activity room
		"""
		try:
			newActivity=None
			if ActivityRoom.LIKE == int(data.get("type_activity")):
				query_activity=ActivityRoom.objects.filter(profile=data.get("profile"),typeroom_id=data.get("typeroom_id"),type_activity=data.get("type_activity"))
				if len(query_activity) == 0:
					newActivity=ActivityRoom(
							typeroom_id=data.get("typeroom_id"),
							by_like=data.get("by_like"),
							profile=data.get("profile"),
							type_activity=data.get("type_activity")
						)
				else:
					update_activity=ActivityRoom.objects.get(pk=query_activity[0].id)
					update_activity.by_like=data.get("by_like")
					update_activity.save()
					log_register=Logs(user=data.get("user"),action=Actions.action_update,name_model='ActivityRoom',id_handle=update_activity.id)
					log_register.save()
					return update_activity.id


			elif ActivityRoom.COMMENT == int(data.get("type_activity")):
				query_activity=ActivityRoom.objects.filter(profile=data.get("profile"),typeroom_id=data.get("typeroom_id"),type_activity=data.get("type_activity"))
				if len(query_activity) == 0:
					newActivity=ActivityRoom(
							typeroom_id=data.get("typeroom_id"),
							comment=data.get("comment"),
							profile=data.get("profile"),
							type_activity=data.get("type_activity")
						)
				else:
					return -1

			if newActivity is not None:
				newActivity.save()
				log_register=Logs(user=data.get("user"),action=Actions.action_create,name_model='ActivityRoom',id_handle=newActivity.id)
				log_register.save()
				return newActivity.id
			
			return 1

		except Exception as e:
			print(e)
			return 0


class NewGuestSerializer(serializers.Serializer):

	full_name = serializers.CharField(required=True, max_length=250)
	date_birth = serializers.CharField(required=True, max_length=250)
	gender = serializers.CharField(required=True, max_length=250)
	type_document_id = serializers.CharField(required=True, max_length=250)
	number_document = serializers.CharField(required=True, max_length=250)
	email = serializers.CharField(required=True, max_length=250)
	phone = serializers.CharField(required=True, max_length=250)
	date_initial = serializers.CharField(required=True, max_length=250)
	date_end = serializers.CharField(required=True, max_length=250)
	type_room_id = serializers.CharField(required=True, max_length=250)
	description=serializers.CharField(required=True, max_length=250,allow_blank=True,allow_null=True)

	def create(self, data):
		"""
		this serializers handles new reservation
		"""
		try:

			sw=0
			room=TypeRoom.objects.get(pk=data.get("type_room_id"))

			if data.get("date_initial") != "" and data.get("date_initial") != "":
				query_reservation=Reservation.objects.filter(type_room_id=data.get("type_room_id"),
					date_initial__range=[data.get("date_initial"),data.get("date_end")],
					date_end__range=[data.get("date_initial"),data.get("date_end")])
				
				review=int(room.enable) - len(query_reservation)
				if review <= 0:
					sw=1

			if sw == 1:
				return -1

			newGuest=Guest(
					full_name=data.get("full_name"),
					date_birth=data.get("date_birth"),
					gender=data.get("gender"),
					type_document_id=data.get("type_document_id"),
					number_document=data.get("number_document"),
					email=data.get("email"),
					phone=data.get("phone")
			)

			newGuest.save()

			log_register=Logs(user=data.get("user"),action=Actions.action_create,name_model='Guest',id_handle=newGuest.id)
			log_register.save()


			newReservation=Reservation(
					guest=newGuest,
					type_room_id=data.get("type_room_id"),
					date_initial=data.get("date_initial"),
					date_end=data.get("date_end"),
					description=data.get("description")
			)
			newReservation.save()

			log_register=Logs(user=data.get("user"),action=Actions.action_create,name_model='Reservation',id_handle=newReservation.id)
			log_register.save()
			
			return newReservation.id

		except Exception as e:
			print(e)
			return 0
