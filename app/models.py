# models.py
from django.db import models
from django.contrib.auth.models import User

class SustainabilityProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    industry=models.FileField(max_length=100)
    
    # Carbon metrics
    carbon_score = models.FloatField(default=0)
    electricity_usage = models.FloatField(default=0)
    gas_consumption = models.FloatField(default=0)
    
    # Energy metrics
    energy_total = models.FloatField(default=0)
    electricity_kwh = models.FloatField(default=0)
    
    # Waste metrics
    total_waste = models.FloatField(default=0)
    waste_reduction_rate = models.FloatField(default=0)
    recycled_waste = models.FloatField(default=0)
    
    # EEVTA metrics
    eevta_score = models.FloatField(default=0)
    total_students = models.IntegerField(default=0)
    tech_voc_percentage = models.FloatField(default=0)
    
    # Financial metrics
    roi = models.FloatField(default=0)
    cost_benefit = models.FloatField(default=0)
    sustainability_score = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class CalculationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(SustainabilityProfile, on_delete=models.CASCADE)
    
    # Input values
    carbon_emissions = models.FloatField()
    energy_consumption = models.FloatField()
    waste_production = models.FloatField()
    eevta_score = models.FloatField()
    revenue = models.FloatField()
    costs = models.FloatField()
    investment = models.FloatField()
    
    # Results
    sustainability_score = models.FloatField()
    roi = models.FloatField()
    cost_benefit = models.FloatField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Calculation Histories'

    def __str__(self):
        return f"{self.user.username}'s calculation at {self.created_at}"