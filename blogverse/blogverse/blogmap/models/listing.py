from django.db import models
from datetime import datetime

class Listing(models.Model):
    date = models.DateTimeField(blank=True,null=True)
    url = models.URLField(blank=False,null=False, max_length=512)
    title = models.CharField(blank=True,null=True, max_length=1024)
    domain = models.ForeignKey('Domain',
                              null=False, 
                              on_delete = models.CASCADE)
    links = models.ManyToManyField('self', through='Linkage', symmetrical=False)
    crawled = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
                models.Index(fields=["url"], name="listing_url_index")
                ]
