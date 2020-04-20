from django.db import models

# Create your models here.
class AccessCodes(models.Model):
    access_code=models.CharField(max_length=7,unique=True,blank=True)
    time_gen=models.DateTimeField(auto_now=True)
    status=models.BooleanField(default=False)




    class Meta:
        db_table='access_codes'

