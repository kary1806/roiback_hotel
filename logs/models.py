from django.db import models
from django.contrib.auth.models import User
from datetime import *
from django.utils import timezone


# Create your models here.

class Logs(models.Model):
	date_create=models.DateTimeField(auto_now_add=True)
	user=models.ForeignKey(User,related_name="logs_usuario",on_delete=models.PROTECT)
	action=models.CharField(max_length=250)
	name_model=models.CharField(max_length=250)
	id_handle=models.IntegerField()

	def __unicode__(self):
		return self.nombre_modelo

#	class Meta:  
#  		 db_table = 'logs.logs'

class Actions():
	action_create='Create'
	action_update='Update'
	action_delete='Delete'

	

