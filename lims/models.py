from django.db import models
from phone_field import PhoneField
from cualid import create_ids
import datetime

# Create your models here.
class Researcher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone = PhoneField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        ordering = ("name", )

    def __str__(self):
        return self.name
   

class Neighborhood(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    def __str__(self):
       return self.name


class Location(models.Model):
    CONSENT_STATUS = [
        ('Consented', 'Consented'),
        ('Not Consented', 'Not Consented'),
        ('Withdrawn', 'Withdrawn'),
        ('Inactive', 'Inactive')
    ]
    name = models.CharField(max_length=100, unique=True)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.PROTECT, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = PhoneField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    consent_status = models.CharField(max_length=15, choices=CONSENT_STATUS, default='Consented')
    consent_date = models.DateField(null=True, blank=True)
    withdrawn_date = models.DateField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name



class Subject(models.Model):

    SEX_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ]
 
    CONSENT_STATUS = [
        ('Consented', 'Consented'),
        ('Not Consented', 'Not Consented'),
        ('Withdrawn', 'Withdrawn'),
        ('Inactive', 'Inactive')
    ]

    given_name = models.CharField(max_length=100, null=True, blank=True)
    family_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    consent_status = models.CharField(max_length=15, choices=CONSENT_STATUS, default='Consented')
    consent_date = models.DateField(null=True, blank=True)
    withdrawn_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = PhoneField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    notes = models.CharField(max_length=300, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        ordering = ("location", "created_on", )
        unique_together = ('given_name', 'family_name',)
        
    def __str__(self):
        return " ".join([n for n in [self.given_name, self.family_name] if n])


class Event(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    researcher = models.ManyToManyField(Researcher, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        ordering = ("-start_date", )
    
    def __str__(self):
        return str(self.name)

    @property
    def is_complete(self):
        """
        Check if current date is after collection date
        """
        return self.start_date < datetime.datetime.now().date()
    

class Animal(models.Model):
    name = models.CharField(max_length=32, null=True, blank=True)
    def __str__(self):
        return str(self.name) 


class HouseSurvey(models.Model):
    HOUSING_CHOICES = [
        ('Cane', 'Cane'),
        ('Palm', 'Palm'),
        ('Adobe', 'Adobe'),
        ('Cement', 'Cement'),
        ('Block', 'Block'),
        ('Wood', 'Wood'),
        ('Mixed', 'Mixed'),
        ('Other', 'Other')
    ]
    WATER_SOURCES = [
        ('Public Network', 'Public Network'),
        ('Delivery Truck', 'Delivery Truck'),
        ('River/Stream', 'River/Stream'),
        ('Ditch', 'Ditch'),
        ('Canal', 'Canal'),
        ('Albarrada', 'Albarrada'),
        ('Embankment', 'Embankment'),
        ('Other', 'Other')
    ]
    WASTE_MANAGEMENT = [
        ('No Toilet', 'No Toilet'),
        ('Cesspool', 'Cesspool'),
        ('Public Sewage System', 'Public Sewage System'),
        ('Discharge to River/Stream', 'Discharge to River/Stream'),
        ('Septic Tank', 'Septic Tank'),
        ('Latrine', 'Latrin'),
        ('Outhouse', 'Outhouse')
    ]
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    owner_of_dwelling = models.BooleanField(null=True, blank=True)
    number_of_residents = models.PositiveIntegerField(null=True, blank=True)
    number_of_residents_sampled = models.PositiveIntegerField(null=True, blank=True)
    type_of_housing = models.CharField(max_length=16, choices=HOUSING_CHOICES, blank=True, null=True)
    housing_condition_note = models.CharField(max_length=128, null=True, blank=True)
    animals_in_backyard = models.BooleanField(null=True, blank=True)
    animal_types = models.ManyToManyField(Animal, blank=True)
    dry_food_stored_near_home = models.BooleanField(null=True, blank=True)
    type_of_dry_food_stored_near_home = models.CharField(max_length=32, null=True, blank=True)
    drinking_water_source = models.CharField(max_length=32, choices=WATER_SOURCES, blank=True, null=True)
    drinking_water_source_notes = models.CharField(max_length=128, null=True, blank=True)
    washing_water_source = models.CharField(max_length=32, choices=WATER_SOURCES, blank=True, null=True)
    washing_water_source_notes = models.CharField(max_length=128, null=True, blank=True)
    waste_management = models.CharField(max_length=32, choices=WASTE_MANAGEMENT, blank=True, null=True)
    waste_management_notes = models.CharField(max_length=128, null=True, blank=True)
    flooding = models.BooleanField(null=True, blank=True)
    flooding_notes = models.CharField(max_length=128, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)


class AnimalSurvey(models.Model):

    ANIMAL_PRODUCT = [
        ('Meat', 'Meat'),
        ('Offspring', 'Offspring'),
        ('Milk', 'Milk'),
        ('Eggs', 'Eggs'),
        ('Other', 'Other')
    ]
    ANIMAL_DISPOSAL = [
        ('Food', 'Food'),
        ('Buried', 'Buried'),
        ('Sold', 'Sold'),
        ('River', 'River'),
        ('Other', 'Other')
    ]
    SACRIFICED_LOCATION = [
        ('House', 'House'),
        ('Municipal Slaughterhouse', 'Municipal Slaughterhouse'),
        ('Clandestine Slaughterhouse', 'Clandestine Slaughterhouse'),
        ('Other', 'Other')
    ]
    MEAT_USE = [
        ('Self-consumption', 'Self-consumption'),
        ('Sold', 'Sold'),
        ('Combination', 'Combination')
    ]
    WATER_SOURCES = [
        ('Public Network', 'Public Network'),
        ('Delivery Truck', 'Delivery Truck'),
        ('River/Stream', 'River/Stream'),
        ('Ditch', 'Ditch'),
        ('Canal', 'Canal'),
        ('Albarrada', 'Albarrada'),
        ('Embankment', 'Embankment'),
        ('Other', 'Other')
    ]

    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT)
    number_of_animals = models.PositiveIntegerField(null=True, blank=True)
    number_sampled = models.PositiveIntegerField(null=True, blank=True)
    feed_type = models.CharField(max_length=64, blank=True, null=True)
    product = models.CharField(max_length=32, choices=ANIMAL_PRODUCT, blank=True, null=True)
    number_died = models.PositiveIntegerField(null=True, blank=True)
    cause_of_death = models.CharField(max_length=128, blank=True, null=True)
    disposal = models.CharField(max_length=16, choices=ANIMAL_DISPOSAL, blank=True, null=True)
    number_sacrificed = models.PositiveIntegerField(null=True, blank=True)
    where_sacrificed = models.CharField(max_length=64, choices=SACRIFICED_LOCATION, blank=True, null=True)
    sacrifice_notes = models.CharField(max_length=128, blank=True, null=True)
    slaughter_frequency = models.CharField(max_length=64, blank=True, null=True)
    meat_destination = models.CharField(max_length=32, choices=MEAT_USE, blank=True, null=True)
    sold_standing = models.BooleanField(null=True, blank=True)
    vet_care = models.BooleanField(null=True, blank=True)
    vet_care_frequency = models.CharField(max_length=32, blank=True, null=True)
    vet_care_notes = models.CharField(max_length=128, blank=True, null=True)
    drinking_water_source = models.CharField(max_length=32, choices=WATER_SOURCES, blank=True, null=True)
    drinking_water_source_notes = models.CharField(max_length=128, null=True, blank=True)
    cleaning_water_source = models.CharField(max_length=32, choices=WATER_SOURCES, blank=True, null=True)
    cleaning_water_source_notes = models.CharField(max_length=128, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)


class ResidentSurvey(models.Model):
    RAT_FREQUENCY = [
        ('None', 'None'),
        ('1-2 days per week', '1-2 days per week'),
        ('3-4 days per week', '3-4 days per week'),
        ('5-6 days per week', '5-6 days per week'),
        ('Every day per week', 'Every day per week'),
        ('Occasionally', 'Occasionally')
    ]

    ACTION_FREQUENCY = [
        ('Always', 'Always'),
        ('Most of the time', 'Most of the time'),
        ('Some of the time', 'Some of the time'),
        ('Never', 'Never')
    ]
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    years_of_residency = models.PositiveIntegerField(null=True, blank=True)
    months_of_residency = models.PositiveIntegerField(null=True, blank=True)
    visited_water_source = models.BooleanField(null=True, blank=True)
    contact_with_water_source = models.BooleanField(null=True, blank=True)
    name_of_visited_water_source = models.CharField(max_length=128, blank=True, null=True)
    location_of_visited_water_source = models.CharField(max_length=128, blank=True, null=True)
    visited_water_source_notes = models.CharField(max_length=128, blank=True, null=True)
    barefoot_near_water_source = models.BooleanField(null=True, blank=True)
    animals_near_water_source = models.BooleanField(null=True, blank=True)
    type_of_animal_near_water_source = models.ManyToManyField(Animal, blank=True, related_name='+')
    rats_near_house = models.BooleanField(null=True, blank=True)
    rats_near_house_day = models.BooleanField(null=True, blank=True)
    rats_near_house_night = models.BooleanField(null=True, blank=True)
    rat_frequency = models.CharField(max_length=32, choices=RAT_FREQUENCY, blank=True, null=True)
    rats_notes = models.CharField(max_length=128, blank=True, null=True)
    animal_contact = models.BooleanField(null=True, blank=True)
    animal_contact_frequency = models.CharField(max_length=128, blank=True, null=True)
    animal_contact_type = models.ManyToManyField(Animal, blank=True, related_name='+')
    barefoot_around_house = models.CharField(max_length=32, choices=ACTION_FREQUENCY, blank=True, null=True)
    barefoot_around_house_notes = models.CharField(max_length=128, blank=True, null=True)
    boil_water = models.CharField(max_length=32, choices=ACTION_FREQUENCY, blank=True, null=True)
    boil_water_notes = models.CharField(max_length=128, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)





class SampleBox(models.Model):
    box_name = models.CharField(max_length=100, unique=True)
    size = models.PositiveIntegerField(default=100)
    storage_location = models.CharField(max_length=100, blank=True, null=True)
    storage_shelf = models.CharField(max_length=100, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        ordering = ("-created_on", )
        verbose_name_plural = "sample_boxes"

    def __str__(self):
        return str(self.box_name)

    def number_of_samples_in_box(self):
        return self.positions.filter(sample__isnull=False).count()

    def is_full(self):
        return self.number_of_samples_in_box() >= self.size
    
    def remaining(self):
        return self.size - self.number_of_samples_in_box()

    def get_next_empty_position(self):
        next_pos = self.positions.filter(sample__isnull=True).order_by('position').first()
        if next_pos:
            return next_pos.id
        else:
            return None
        



class Sample(models.Model):
    COLLECTION_CHOICES = [
    ('Collected', 'Collected'),
    ('Not Collected', 'Not Collected'),
    ('Pending', 'Pending'),
    ('Refused', 'Refused')
    ]
    SAMPLE_TYPE = [
        ('Urine', 'Urine'),
        ('Water', 'Water'),
        ('Soil', 'Soil'),
        ('Trap', 'Trap'),
        ('Carcass', 'Carcass')
    ]
    SAMPLE_SOURCE = [
        ('Human', 'Human'),
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Rat', 'Rat'),
        ('Mouse', 'Mouse'),
        ('Horse', 'Horse'),
        ('Cow', 'Cow'),
        ('Donkey', 'Donkey'),
        ('Pig', 'Pig'),
        ('Environment', 'Environment')
    ]

    name = models.CharField(max_length=8, unique=True)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, null=True, blank=True)
    source = models.CharField(max_length=15, choices=SAMPLE_SOURCE, null=True, blank=True)
    sample_type = models.CharField(max_length=15, choices=SAMPLE_TYPE, null=True, blank=True)
    collection_event = models.ForeignKey(Event, on_delete=models.PROTECT)
    collection_status = models.CharField(max_length=15, choices=COLLECTION_CHOICES, default='Pending')
    notes = models.TextField(blank=True, null=True)
    shipped_date = models.DateField(null=True, blank=True)
    box = models.ForeignKey(SampleBox, on_delete=models.PROTECT, null=True, blank=True)
    box_position = models.IntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    
    class Meta:
        ordering = ("subject", "collection_event", "sample_type")
        constraints = [
        models.UniqueConstraint(fields=["box", "box_position"], name='unique_box_position')
        ]
    
    def __str__(self):
        return str(self.name)
    
    def get_samples_for_event(event):
        samples = Sample.objects.filter(collection_event=event).order_by(
            'name')
        return samples

    

class Sequencing(models.Model):
    name = models.CharField(max_length=100, unique=True)
    run_id = models.CharField(max_length=100, null=True, blank=True)
    samples = models.ManyToManyField(Sample, blank=True)
    protocol = models.TextField(null=True, blank=True)
    targets = models.CharField(max_length=100, null=True, blank=True)
    researcher = models.ManyToManyField(Researcher, blank=True)
    prep_url = models.TextField(null=True, blank=True)
    seq_loc = models.TextField(null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        ordering = ("-created_on", )

    def __str__(self):
        return str(self.name) 
   

class Test(models.Model):
    name = models.CharField(max_length=100, unique=True)
    lab = models.CharField(max_length=100, null=True, blank=True)
    protocol = models.TextField(null=True, blank=True)
    detects = models.CharField(max_length=100, null=True, blank=True)
    threshold = models.FloatField(default=40, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        ordering = ("-created_on", )

    def __str__(self):
        return str(self.name)



class SampleResult(models.Model):
    RESULT_CHOICES = [
    ('Positive', 'Positive'),
    ('Negative', 'Negative'),
    ('Pending', 'Pending'),
    ('Undetermined', 'Undetermined'),
    ]

    sample = models.ForeignKey(Sample, on_delete=models.PROTECT)
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    result = models.CharField(max_length=15, choices=RESULT_CHOICES, default='Pending')
    value = models.FloatField(null=True, blank=True)
    researcher = models.ManyToManyField(Researcher, blank=True)
    notes = models.TextField(blank=True, null=True)
    run_date = models.DateField(null=False, blank=False, default=datetime.date.today) # Required field
    run_name = models.CharField(max_length=64, null=False, blank=False, default="Run1")
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        ordering = ("-created_on",)

    def __str__(self):
        return "{0}_{1}_{2}".format(self.sample.name, self.test, self.run_name)
    

class Label(models.Model):
    PAPERSIZE_CHOICES = [
    ('LETTER', 'Letter'),
    ('A4', 'A4')
    ]
    name = models.CharField(max_length=100, unique=True)
    paper_size = models.CharField(max_length=15, choices=PAPERSIZE_CHOICES, default='Letter')
    top_margin = models.FloatField()
    left_margin = models.FloatField()
    label_width = models.FloatField()
    label_height = models.FloatField()
    columns = models.PositiveIntegerField()
    rows = models.PositiveIntegerField()
    row_margin = models.FloatField()
    col_margin = models.FloatField()
    top_padding = models.FloatField()
    left_padding = models.FloatField()
    max_chars = models.PositiveIntegerField(default=25)
    font_size = models.FloatField(default=7)
    qr_size = models.FloatField(default=12)
    line_spacing = models.FloatField(default=2.3)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        ordering = ("-created_on",)

    def __str__(self):
        return str(self.name)