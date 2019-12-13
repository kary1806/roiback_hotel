from django.contrib import admin
from logs.models import Logs
# Register your models here.

class AdminLogs(admin.ModelAdmin):
	list_display=('date_create','user','action','name_model','id_handle')
	search_fields=('user','action','name_model','id_handle')
	list_filter=('user','action','name_model','id_handle')

admin.site.register(Logs,AdminLogs)	
