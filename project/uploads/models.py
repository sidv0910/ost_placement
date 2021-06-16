from django.db import models

def cv_convert(instance, filename):
    print(filename)
    if filename.split('.')[-1] == "pdf":
        return 'cv/'
    else:
        return 'cv/{0}'.format(str(instance.email) + ".pdf")

class Profile(models.Model):
    email = models.EmailField(primary_key=True)
    contact = models.IntegerField()
    cv = models.FileField(upload_to=cv_convert)