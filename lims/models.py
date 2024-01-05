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
    protocol = models.TextField(null=True, blank=True)
    detects = models.CharField(max_length=100, null=True, blank=True)
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
    ('Unknown', 'Unknown'),
    ('Inconclusive', 'Inconclusive')
    ]

    sample = models.ForeignKey(Sample, on_delete=models.PROTECT)
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    replicate = models.PositiveIntegerField(default=1)
    result = models.CharField(max_length=15, choices=RESULT_CHOICES, default='Pending')
    value = models.CharField(max_length=100, null=True, blank=True)
    researcher = models.ManyToManyField(Researcher, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        ordering = ("-created_on",)
        # contrant that prevents duplicate sample results
        constraints = [
        models.UniqueConstraint(fields=["sample", "test", "replicate"], name='unique_sample_result')
        ]

    def __str__(self):
        return "{0}_{1}_{2}".format(self.sample.name, self.test, self.replicate)
    

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