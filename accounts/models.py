from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import models

# Create your models here.

class Search(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    search_group=models.CharField(max_length=20,null=False,blank=False)
    search_term=models.CharField(max_length=20,null=True,blank=True)

    class Meta:
        db_table='user_search'

class Messages(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE)
    receiver=models.ForeignKey(User,on_delete=models.CASCADE,related_name='receiver')
    message_text=models.CharField(max_length=255,blank=False,null=False)
    created_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='messages'
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_image_name=models.CharField(max_length=50,blank=False,null=True)

    class Meta:
        db_table='user_profile'


# Create your models here.
class LoggedInUser(models.Model):
    user=models.OneToOneField(User,related_name='logged_in_user',on_delete=models.CASCADE)
    session_key=models.CharField(max_length=32,blank=True,null=True)

    def __str__(self):
        return  self.user.username

#Model to store user session data.
class UserSession(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    session=models.ForeignKey(Session,on_delete=models.CASCADE)

    class Meta:
        db_table='user_session'

