from blogmap.models import Domain
from django.db import models
from datetime import datetime


class Listing(models.Model):
    date = models.DateTimeField(blank=True,null=True)
    url = models.URLField(blank=False,null=False, max_length=512)
    title = models.CharField(blank=True,null=True, max_length=1024)
    domain = models.ForeignKey(Domain,
                              null=False, 
                              on_delete = models.CASCADE)
    links = models.ManyToManyField('Listing')#Assuming that we can filter external and internal links by chaining.
    crawled = models.BooleanField(default=False)

    def __str__(self):
        return self.title

