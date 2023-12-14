from django.db import models

class DBTable(models.Model):
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)

class Cname(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    cname = models.CharField(max_length=255)
    ttl = models.IntegerField()
    # type = models.CharField(max_length=10)
    last_modified = models.DateTimeField(auto_now=True)
    # associated_distribution = models.ForeignKey(Distribution, on_delete=models.CASCADE, null=True, blank=True)
    associated_distribution = models.CharField(max_length=255, default="No distribution")

    class Meta:
        unique_together = ('domain', 'cname')

    def __str__(self):
        return f"{self.cname} ({self.domain_name})"

class Inventory(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    vendor = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    domain_name = models.CharField(max_length=255)
    regions = models.CharField(max_length=255)
    origins = models.CharField(max_length=255)
    state = models.CharField(max_length=255)    
    status = models.CharField(max_length=255)
    last_modified = models.DateField()
