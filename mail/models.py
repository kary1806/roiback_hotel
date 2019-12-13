from django.db import models
# from django.core.mail import EmailMessage
from django.core import mail
from datetime import datetime
# Create your models here.
class Message(models.Model):
	remitente =  models.EmailField()
	destinatario = models.TextField()
	asunto = models.CharField(max_length=255)
	contenido = models.TextField()
	enviado = models.BooleanField(default=False)
	horaPreparacion = models.DateTimeField(auto_now_add=True, blank=True)
	horaEnvio = models.DateTimeField(blank=True,null=True)

	def __unicode__(self):
		return self.asunto

	#envio de correos simple sin copias, 1 remitente, 1 destinatario	
	def simpleSend(self):
		connection = mail.get_connection()
		res=''
		email = mail.EmailMessage(
			self.asunto,
			self.contenido,
			self.remitente,
			[self.destinatario]
			)
		email.content_subtype = "html"
		res=connection.send_messages([email])
		connection.close()
		# res =email.send()
		print(res)
		#res = send_mail(self.asunto,self.contenido,self.remitente,[self.destinatario],fail_silently=False)
		if res ==1:
			self.enviado=True
			self.horaEnvio = datetime.now()
			self.save()

		return res



			
