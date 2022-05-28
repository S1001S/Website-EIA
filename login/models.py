from xml.etree.ElementInclude import default_loader
from django.db import models

class Criminal(models.Model):
    firstname=models.CharField(max_length=100)
    lastname=models.CharField(max_length=100)
    criminalid=models.CharField(max_length=100,default="")
    age=models.CharField(max_length=100,default="")
    gender=models.CharField(max_length=100,default="")
    residence=models.CharField(max_length=1000,default="")
    crime=models.CharField(max_length=10000,default="")
    picture=models.ImageField(upload_to='login/criminals/images', default="")

    def __str__(self):
        return self.firstname+self.criminalid

class Missing(models.Model):
    name=models.CharField(max_length=100)
    age=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)
    contactperson=models.CharField(max_length=100)
    contactnumber=models.CharField(max_length=100)
    picture=models.ImageField(upload_to='login/missing/images', default="")
    foundpicture=models.ImageField(upload_to='login/missing_found/images', default="")
    foundby=models.CharField(max_length=100, default="")

    def __str__(self):
        return self.name+"_"+self.contactnumber

class Report(models.Model):
    report_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    mobile=models.CharField(max_length=100)
    aadhar=models.CharField(max_length=100)
    gender=models.CharField(max_length=100,default="")
    residence=models.CharField(max_length=1000,default="")
    description=models.CharField(max_length=10000,default="")
    picture1=models.ImageField(upload_to='login/report/images', default="", blank=True)
    picture2=models.ImageField(upload_to='login/report/images', default="", blank=True)
    picture3=models.ImageField(upload_to='login/report/images', default="", blank=True)
    video=models.FileField(upload_to='login/report/videos', default="", blank=True)

    def __str__(self):
        return self.name+"_"+self.aadhar

class ReportUpdate(models.Model):
    update_id=models.AutoField(primary_key=True)
    report_id=models.IntegerField(default=0)
    update_desc=models.CharField(max_length=6000)
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:20]+"......"

class CriminalUpdate(models.Model):
    update_id=models.AutoField(primary_key=True)
    criminalid=models.IntegerField(default=0)
    update_crime=models.CharField(max_length=6000)
    update_locations=models.CharField(max_length=6000)
    timestamp=models.DateTimeField(auto_now_add=True)
    lat=models.DecimalField(max_digits=9, decimal_places=6,null=True, blank=True)
    lng=models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    time=models.TimeField(null=True)

    def __str__(self):
        return str(self.criminalid)+"_"+self.update_crime[0:20]+"......"

class PoliceDetail(models.Model):
    police_id=models.AutoField(primary_key=True)
    username=models.CharField(max_length=100, default="")
    firstname=models.CharField(max_length=100, default="")
    lastname=models.CharField(max_length=100, default="")
    email=models.CharField(max_length=100,default="")
    picture=models.ImageField(upload_to='login/police/images', default="")

    def __str__(self):
        return str(self.username)


