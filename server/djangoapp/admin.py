from django.contrib import admin
from .models import CarMake, CarModel


class CarModelInline(admin.StackedInline):
    model = CarModel

# CarModelAdmin class


class CarModelAdmin(admin.ModelAdmin):
    fields = ['dealer_id', 'name', 'type', 'year']

# CarMakeAdmin class with CarModelInline


class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    extra = 1


# Register models here
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(CarMake, CarMakeAdmin)
