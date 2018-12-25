from django.db import models


class Domain(models.Model):
    name = models.CharField(blank=True, 
                            default='',
                            max_length=255)
    author = models.CharField(blank=True,
                             default='',
                             max_length=50)
    url = models.URLField(blank=False, null=False)

    crawled = models.BooleanField(default=False)
                                 
    def __str__(self):
        return (self.name)

    def get_url(self):
        return self.url
