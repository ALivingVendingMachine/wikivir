from django.db import models

# Create your models here.
class Topic(models.Model):
    def __str__(self):
        return self.topicTitle
    
    topicTitle = models.CharField(max_length=256)
    topicBody = models.CharField(max_length=2560)
    relatedSamples = models.ManyToManyField('MalwareSample')
    categoriesChoices = (
        ("TE", "Technique"),
        ("AP", "APT"),
        ("SA", "Sample"),
        ("NO", "None"),
    )
    category = models.CharField(max_length=2, choices=categoriesChoices, default="NO")
    #TODO: first user or similar?

class MalwareSample(models.Model):
    def __str__(self):
        return self.fileHash

    fileHash = models.CharField(max_length=256)
    fileBlob = models.FileField()
    date = models.DateField(auto_now=True)
    ready = models.BooleanField(default=False)
    file = models.CharField(max_length=2560)
    readelf = models.CharField(max_length=2560000)
    objdump = models.CharField(max_length=2560000)
    relatedTopics = models.ManyToManyField(Topic)

