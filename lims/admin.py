from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import (
    Sample, SampleBox, 
    Location, Neighborhood, Sequencing,
    Researcher, Event, Label,
    Test, SampleResult, HouseSurvey, AnimalSurvey,
    ResidentSurvey, Animal 
)

@admin.register(Sample, SampleBox,
    Location, Neighborhood, Sequencing,
    Researcher, Event, Label,
    Test, SampleResult, ResidentSurvey, HouseSurvey,
    Animal, AnimalSurvey)
class ViewAdmin(ImportExportModelAdmin):
    pass