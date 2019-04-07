from django.db import models

# Create your models here.
class MalwareSample(models.Model):
    def __str__(self):
        return self.fileHash
    fileHash = models.CharField(max_length=256)
    filePath = models.CharField(max_length=256)
    file = models.FileField(upload_to='samples/')
    date = models.DateField(auto_now=True)

class Topic(models.Model):
    def __str__(self):
        return self.topicTitle
    
    topicTitle = models.CharField(max_length=256)
    topicBody = models.CharField(max_length=2560)
    #TODO: first user or similar?
