from django.db import models

class Linkage(models.Model):
    source = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='link_source')
    destination = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='link_destination')
    frequency = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(max_digits=6,decimal_places=3, default=0.0)

