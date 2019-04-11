from django.db import models
from taggit.managers import TaggableManager

# Create your models here.
class MalwareSample(models.Model):
    def __str__(self):
        return self.fileHash
    fileHash = models.CharField(max_length=256)
    fileBlob = models.FileField()
    date = models.DateField(auto_now=True)
    ready = models.BooleanField(default=False)
    file = models.CharField(max_length=2560)
    readelf = models.CharField(max_length=256000)
    objdump = models.CharField(max_length=256000)
    tags = TaggableManager()

class Topic(models.Model):
    def __str__(self):
        return self.topicTitle
    
    topicTitle = models.CharField(max_length=256)
    topicBody = models.CharField(max_length=2560)
    tags = TaggableManager()
    #TODO: first user or similar?
