from django.db import models

class Offer(models.Model):
    offer_title = models.CharField(max_length=200, null=True)
    company_name = models.CharField(max_length=200, null=True)
    location = models.CharField(max_length=70, null=True)
    employment_type = models.CharField(max_length=30, null=True)
    min_salary = models.IntegerField(null=True)
    max_salary = models.IntegerField(null=True)
    link = models.URLField()
    contract_type = models.CharField(max_length=100, null=True, blank=True)
    seniority = models.CharField(max_length=50, null=True)
