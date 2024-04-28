from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Talk(models.Model):
    message=models.CharField(max_length=500)
    sender=models.ForeignKey(
        User,on_delete=models.CASCADE,related_name="send_talk"
    )
    receiver=models.ForeignKey(
        User,on_delete=models.CASCADE,related_name="received_talk"
    )
    time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} -> {}".format(self.sender,self.receiver)
