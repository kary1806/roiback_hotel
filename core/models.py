from django.db import models
from django.conf import settings
from django.contrib.auth.models import User 

# Create your models here.


class TypeDocument(models.Model):

	NATURAL = 1
	BUSINESS = 2

	TYPE_USER = ((NATURAL, "Natural"),(BUSINESS, "Empresa"))

	name=models.CharField(max_length=340)
	inicial=models.CharField(max_length=340,null=True,blank=True)
	type_user = models.PositiveSmallIntegerField("Tipo de Usuario", choices=TYPE_USER)

	def __str__(self): 
		return self.name


class City(models.Model):

	name=models.CharField(max_length=340)
	inicial=models.CharField(max_length=340,null=True,blank=True)

	def __str__(self): 
		return self.name


class Profile(models.Model):
	#estado del perfil
	ACTIVE = 1
	INACTIVE = 2

	STATUS_PROFILE = ((ACTIVE, "Activo"),(INACTIVE, "Inactivo"))

	# Sexo
	NONE = 0
	FEMALE = 1
	MALE= 2

	GENDER = ((NONE, "Ninguno"),(FEMALE, "Femenino"), (MALE, "Masculino"))

	type_document= models.ForeignKey(TypeDocument,limit_choices_to={'type_user': TypeDocument.NATURAL}, verbose_name='TypeDocument', on_delete=models.PROTECT, related_name='profile_type_document')
	number_document = models.CharField(max_length=340, null=True, blank=True)
	person_status = models.PositiveSmallIntegerField("Estado de la persona", choices=STATUS_PROFILE,default=ACTIVE)
	user 	= 	models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	gender= models.PositiveSmallIntegerField("Género", choices=GENDER,default=NONE)
	phone = models.BigIntegerField(null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	date_birth=models.DateField(null=True, blank=True)

	def __str__(self): 
		return self.user.username


class Category(models.Model):
	name = models.CharField(max_length=340)
	date_created = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	def __str__(self): 
		return self.name


class Tags(models.Model):
	name = models.CharField(max_length=340)
	date_created = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	def __str__(self): 
		return self.name


class Hotel(models.Model):

	#estado del hotel
	ACTIVE = 1
	INACTIVE = 2

	STATUS_HOTEL = ((ACTIVE, "Activo"),(INACTIVE, "Inactivo"))

	name = models.CharField(max_length=340)
	type_document= models.ForeignKey(TypeDocument,limit_choices_to={'type_user': TypeDocument.BUSINESS}, verbose_name='TypeDocument', on_delete=models.PROTECT, related_name='hotel_type_document')
	number_document = models.CharField(max_length=340, null=True, blank=True)
	owner= models.ForeignKey(Profile,verbose_name='Profile', on_delete=models.PROTECT, related_name='profile_hotel')
	category =models.ManyToManyField(Category,verbose_name="Category")
	tags =models.ManyToManyField(Tags,verbose_name="Tags")
	status = models.PositiveSmallIntegerField("Estado del hotel", choices=STATUS_HOTEL,default=ACTIVE)
	date_created = models.DateTimeField(auto_now_add=True)
	date_publish = models.DateField(null=True, blank=True)
	date_inactive = models.DateField(null=True, blank=True)
	city= models.ForeignKey(City,verbose_name='City', on_delete=models.PROTECT, related_name='city_hotel',null=True,blank=True)

	def __str__(self): 
		return self.name



class ActivityHotel(models.Model):

	#estado del hotel
	NONE=0
	LIKE = 1
	COMMENT = 2

	TYPE_ACTIVITY = ((NONE, "Ninguna"),(LIKE, "Gustar"),(COMMENT, "Comentario"))

	hotel= models.ForeignKey(Hotel,verbose_name='Hotel', on_delete=models.PROTECT, related_name='activity_hotel')
	comment = models.CharField(max_length=340,null=True, blank=True)
	by_like=models.BooleanField(default=False)
	profile= models.ForeignKey(Profile,verbose_name='Profile', on_delete=models.PROTECT, related_name='profile_activity_hotel')
	date_created = models.DateTimeField(auto_now_add=True)
	type_activity = models.PositiveSmallIntegerField("Tipo de Actividad del hotel", choices=TYPE_ACTIVITY,default=NONE)

	def __str__(self): 
		return str(self.type_activity)


class TypeRoom(models.Model):

	#estado del cuarto
	ACTIVE = 1
	INACTIVE = 2

	STATUS_ROOM = ((ACTIVE, "Activo"),(INACTIVE, "Inactivo"))

	name = models.CharField(max_length=340)
	hotel= models.ForeignKey(Hotel,verbose_name='Hotel', on_delete=models.PROTECT, related_name='room_hotel')
	price = models.IntegerField('Precio',default=0)
	count_person = models.IntegerField('Cantidad de Persona',default=0)
	description = models.TextField(null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	status = models.PositiveSmallIntegerField("Estado del cuarto", choices=STATUS_ROOM,default=ACTIVE)
	date_publish = models.DateField(null=True, blank=True)
	date_inactive = models.DateField(null=True, blank=True)
	owner= models.ForeignKey(Profile,verbose_name='Profile', on_delete=models.PROTECT, related_name='profile_room')
	enable = models.IntegerField('Cantidad de disponibilidad',default=0) #cantidad de disponibilidad que tiene esta habitacion

	def __str__(self): 
		return self.name



class ActivityRoom(models.Model):

	#estado del hotel
	NONE=0
	LIKE = 1
	COMMENT = 2

	TYPE_ACTIVITY = ((NONE, "Ninguna"),(LIKE, "Gustar"),(COMMENT, "Comentario"))

	typeroom= models.ForeignKey(TypeRoom,verbose_name='TypeRoom', on_delete=models.PROTECT, related_name='activity_typeroom')
	comment = models.CharField(max_length=340,null=True, blank=True)
	by_like=models.BooleanField(default=False)
	profile= models.ForeignKey(Profile,verbose_name='Profile', on_delete=models.PROTECT, related_name='profile_activity_room')
	date_created = models.DateTimeField(auto_now_add=True)
	type_activity = models.PositiveSmallIntegerField("Tipo de Actividad de cuarto", choices=TYPE_ACTIVITY,default=NONE)

	def __str__(self): 
		return str(self.type_activity)


class Guest(models.Model):
	# Sexo
	NONE = 0
	FEMALE = 1
	MALE= 2

	GENDER = ((NONE, "Ninguno"),(FEMALE, "Femenino"), (MALE, "Masculino"))


	full_name=models.CharField(max_length=340, null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	date_birth=models.DateField(null=True, blank=True)
	gender= models.PositiveSmallIntegerField("Género", choices=GENDER,default=NONE)
	type_document= models.ForeignKey(TypeDocument,limit_choices_to={'type_user': TypeDocument.NATURAL}, verbose_name='TypeDocument', on_delete=models.PROTECT, related_name='guest_type_document')
	number_document = models.CharField(max_length=340, null=True, blank=True)
	email=models.CharField(max_length=340, null=True, blank=True)
	phone = models.BigIntegerField(null=True, blank=True)
	

	def __str__(self): 
		return self.full_name


class Reservation(models.Model):

	guest= models.ForeignKey(Guest,verbose_name='Guest', on_delete=models.PROTECT, related_name='reservation_guest')
	type_room= models.ForeignKey(TypeRoom,verbose_name='TypeRoom', on_delete=models.PROTECT, related_name='reservation_room')
	date_created = models.DateTimeField(auto_now_add=True)
	date_initial = models.DateField(null=True, blank=True)
	date_end = models.DateField(null=True, blank=True)
	description = models.CharField(max_length=340, null=True, blank=True)

	def __str__(self): 
		return self.guest.full_name
