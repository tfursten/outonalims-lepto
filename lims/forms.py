import datetime
import json
from django import forms
from django.forms import ModelForm, CheckboxInput, SelectMultiple
from .models import (
    Sample, Location, Researcher,
    Event, SampleBox, Neighborhood,
    Label, SampleResult, Subject,
    Test, Sequencing, HouseSurvey, AnimalSurvey, ResidentSurvey)
from string import capwords
# from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.forms import widgets



class DateInput(forms.DateInput):
    input_type = 'date'



class LocationForm(ModelForm):
    class Meta:
        model = Location
        exclude = []
        widgets = {
            'consent_date': DateInput(attrs={'type': 'date', 'value': datetime.date.today()}),
            'withdrawn_date': DateInput()
        }


    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        # 

    @staticmethod
    def label_from_instance(obj):
        return "%s" % obj.name
    

class NeighborhoodForm(ModelForm):
    class Meta:
        model = Neighborhood
        exclude = []

    def __init__(self, *args, **kwargs):
        super(NeighborhoodForm, self).__init__(*args, **kwargs)
        # 
        
    @staticmethod
    def label_from_instance(obj):
        return "%s" % obj.name



class ResearcherForm(ModelForm):
    class Meta:
        model = Researcher
        fields = ['name', 'email', 'phone']


class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = []
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['location'].label_from_instance = self.label_from_instance
        self.fields['researcher'].label_from_instance = self.label_from_instance

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("start_date") and cleaned_data.get("end_date"):
            start_date = cleaned_data.get("start_date")
            end_date = cleaned_data.get("end_date")

            if start_date  > end_date:
                error_message = forms.ValidationError("End date must be after start date")
                self.add_error('end_date', error_message)

        return cleaned_data



    @staticmethod
    def label_from_instance(obj):
        return "%s" % obj.name



class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        exclude = []
        widgets = {
            'consent_date': DateInput(),
            'withdrawn_date': DateInput(),
            'birth_date': DateInput
        }
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['location'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return "%s" % obj.name


class SampleForm(ModelForm):
    class Meta:
        model = Sample
        fields = ['subject', 'collection_status', 'sample_type', 'source', 'shipped_date', 'notes']
        widgets = {
            'shipped_date': DateInput(),
        }

class SampleUploadFileForm(ModelForm):
    file = forms.FileField()
    class Meta:
        model = Sample
        fields = []


class SelectEventForm(ModelForm):
    additional_samples = forms.IntegerField(help_text="Samples will be created for all subjects assigned to this event, additional blank samples can be added here.")
    class Meta:
        model = Sample
        fields = ['event', 'additional_samples']
    today = datetime.date.today()
    # Only select events that have not already completed
    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(end_date__gte=today),
        help_text="If an event is not listed it is because the event date has passed and event is completed. If the event date is incorrect, you can edit it on the Event page."
        )

    def __init__(self, *args, **kwargs):
        hide_condition = kwargs.pop('hide_count', None)
        super(SelectEventForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'event' in kwargs['initial']:
                self.fields['event'].value = kwargs['initial']['event']
        if hide_condition:
            del self.fields['additional_samples']




class SamplePrint(forms.Form):    
    start_position = forms.IntegerField(min_value=1, initial=1,
        help_text="Change starting position of the labels on the label sheet. Positions start at 1 and increment down each column.")
    replicates = forms.IntegerField(min_value=1, initial=1,
        help_text="Enter the number of labels to print per sample.", widget = forms.HiddenInput(), required = False)
    label_paper = forms.ModelChoiceField(queryset=Label.objects.all(), initial=1)
    abbreviate = forms.BooleanField(initial=False, required=False)
    


class SampleBoxForm(ModelForm):
    class Meta:
        model = SampleBox
        fields = ['box_name', 'size', 'storage_location', 'storage_shelf']
   


 

class FixIDS(forms.Form):
    sample_id = forms.CharField(
        label="Sample ID", max_length=10,
        help_text="Enter sample ID to correct", required=False)
    # subject_id = forms.CharField(
    #     label="Subject ID", max_length=10,
    #     help_text="Enter subject ID to correct", required=False)


class LabelForm(ModelForm):
    class Meta:
        model = Label
        exclude = ['created_on']
        fields = ['name', 'paper_size', 'rows', 'columns',
        'top_margin', 'left_margin', 'label_width', 'label_height',
        'row_margin', 'col_margin', 'top_padding', 'left_padding', 'font_size',
        'max_chars', 'qr_size', 'line_spacing' ]
    rows = forms.IntegerField(min_value=0, label="Number of Rows")
    columns = forms.IntegerField(min_value=0, label="Number of Columns")
    top_margin = forms.FloatField(min_value=0.0, label="Margin from top of sheet to first row of labels (mm)")
    left_margin = forms.FloatField(min_value=0.0, label="Margin from left of sheet to first column of labels (mm)")
    label_width = forms.FloatField(min_value=0.0, label="Width of labels (mm)")
    label_height = forms.FloatField(min_value=0.0, label="Height of labels (mm)")
    row_margin = forms.FloatField(min_value=0.0, label="Margin between rows of labels (mm)")
    col_margin = forms.FloatField(min_value=0.0, label="Margin between columns of labels (mm)")
    top_padding = forms.FloatField(label="Padding from label top (mm)")
    left_padding = forms.FloatField(label="Padding from left of label (mm)")
    font_size = forms.FloatField(label="Font size for text", initial=7)
    qr_size = forms.FloatField(min_value=5, label="Size of QR code (mm)", initial=12, help_text="Smaller than 5mm x 5mm will not scan")
    max_chars = forms.IntegerField(min_value=10, label="Maximum number of characters per line", initial=25)
    line_spacing = forms.FloatField(label="Spacing between lines (mm)", initial=2.3)

    
class TestForm(ModelForm):
    class Meta:
        model = Test
        fields = ['name', 'lab', 'detects', 'threshold', 'protocol', ]
        labels = {
            'name': 'Test Name',
            'lab': 'Name of lab where test is performed',
            'detects': 'What does the assay target',
            'threshold': 'Threshold for detection',
            'protocol': 'Description of protocol'
        }


class SequenceForm(ModelForm):
    class Meta:
        model = Sequencing
        fields = ['name', 'run_id', 'targets', 'date', 'protocol', 'notes', 'samples']
        widgets = {
            'date': DateInput(),
            'samples': forms.SelectMultiple(attrs={'size': '20'})}
    def __init__(self, *args, **kwargs):
        super(SequenceForm, self).__init__(*args, **kwargs)
        self.fields['samples'].queryset = Sample.objects.filter(collection_status="Collected").order_by("name")





class SampleResultForm(ModelForm):
    class Meta:
        model = SampleResult
        fields = ['sample', 'test', 'result', 'value', 'run_date', 'run_name', 'researcher', 'notes', ]
        widgets = {
            'run_date': DateInput()}
        labels= {
            'value': 'Ct/Cq Value',
            'run_date': 'Date of qPCR Run',
            'run_name': 'Name of qPCR Run (hint: use the filename of the qPCR output to ensure results are not entered multiple times)',
            'researcher': 'Select researcher(s) who performed the qPCR (cmd/ctrl click to select multiple)'
        }

    def __init__(self, *args, **kwargs):
        super(SampleResultForm, self).__init__(*args, **kwargs)

        # Prefill existing sample if editing an instance
        if self.instance and self.instance.pk:
            selected_sample = self.instance.sample
        else:
            selected_sample = None

        # Filter samples to only show collected ones and include the currently selected sample
        queryset = Sample.objects.filter(collection_status="Collected").order_by('name')

        # If editing and a sample is already selected, include it in the queryset
        if selected_sample and selected_sample not in queryset:
            queryset = Sample.objects.filter(pk=selected_sample.pk) | queryset

        self.fields['sample'].queryset = queryset

class EventSelectionForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(), 
        label="Select Event",
        widget=forms.Select(attrs={"class": "form-control"})
    )     

class SampleResultUploadFileForm(ModelForm):
    file = forms.FileField(help_text="Choose file to upload")
    class Meta:
        model = SampleResult
        fields = ['file', 'researcher']
        labels = {
            'researcher': 'Select researcher(s) who performed the qPCR (cmd/ctrl click to select multiple)',
            }


class HouseSurveyForm(ModelForm):
    class Meta:
        model = HouseSurvey
        exclude = []
        labels = {
            "event": "Collection Event",
            "owner_of_dwelling": "Owner of the dwelling",
            "number_or_residents": "Number of residents",
            "number_or_residents_sampled": "Number of residents sampled",
            "type_of_housing": "Type of housing material",
            "housing_condition_note": "Housing condition notes",
            "animals_in_backyard": "Animals in backyard",
            "animal_types": "Types of animals in backyard",
            "dry_food_stored_near_home": "Dry food storage (grain, peanuts, corn, etc) near home",
            "type_of_dry_food_stored_near_home": "Type of dry food stored",
            "drinking_water_source": "Source of drinking water",
            "drinking_water_source_notes": "Drinking water source notes",
            "washing_water_source": "Washing water source",
            "washing_water_source_notes": "Washing water source notes",
            "waste_management": "Type of waste management",
            "waste_management_notes": "Waste management notes",
            "flooding": "Flooding in last month",
            "flooding_notes": "Recent flooding notes",
        }

        widgets = {
            'animal_types': forms.CheckboxSelectMultiple(),
        }
    def __init__(self, *args, **kwargs):
        if 'event' in kwargs:
            event = kwargs.pop('event')
            kwargs.update(initial={
                'event': event
            })
        super(HouseSurveyForm, self).__init__(*args, **kwargs)


class AnimalSurveyForm(ModelForm):
    class Meta:
        model = AnimalSurvey
        exclude = []
        labels = {
            "event": "Collection Event",
            "animal": "Type of animal",
            "number_of_animals": "Number of animals of this type",
            "number_sampled": "Number of this animal type sampled",
            "feed_type": "Type of feed",
            "product": "Animal products",
            "number_died": "Number of this animal that died in last week",
            "cause_of_death": "Cause(s) of death",
            "disposal": "How were dead animals disposed",
            "number_sacrificed": "Number of sacrificed animals of this type",
            "where_sacrificed": "Where were the animals sacrificed",
            "sacrifice_notes": "Animal sacrifice notes",
            "slaughter_frequency": "How often are animals slaughtered",
            "meat_destination": "What is done with the meat",
            "sold_standing": "Are animals sold standing",
            "vet_care": "Do animals have vet care",
            "vet_care_frequency": "How often do they receive vet care",
            "vet_care_notes": "Vet care notes",
            "drinking_water_source": "Where does the animal drinking water come from",
            "cleaning_water_source": "Which water source is used to clean animals/habitat"
        }



    def __init__(self, *args, **kwargs):
        if 'event' in kwargs:
            event = kwargs.pop('event')
            kwargs.update(initial={
                'event': event
            })
        super(AnimalSurveyForm, self).__init__(*args, **kwargs)


class ResidentSurveyForm(ModelForm):
    class Meta:
        model = ResidentSurvey
        exclude = []
        labels = {
            "event": "Collection Event",
            "subject": "Select subject",
            "years_of_residency": "How many years have they lived in home",
            "months_of_residency": "How many months have they lived in home",
            "visited_water_source": "Have they visited rivers, lakes, or natural water sources in the last month",
            "contact_with_water_source": "Did they have contact with the water",
            "name_of_visited_water_source": "Name(s) of the water source(s) visited",
            "location_of_visited_water_source": "Location(s) of the water source(s)",
            "barefoot_near_water_source": "Do they walk barefoot along the edge of the water source",
            "animals_near_water_source": "Were there animals nearby or inside the water source",
            "type_of_animal_near_water_source": "What type of animal(s) were near/inside the water source",
            "rats_near_house": "Have they seen rats/mice around the house",
            "rats_near_house_day": "Have they seen rats/mice around the house during the day",
            "rats_near_house_night": "Have they seen rats/mice around the house during the night",
            "rat_frequency": "How often have they seen rats/mice around the house in the last month",
            "rats_notes": "Other notes about race/mice around the house",
            "animal_contact": "Have they been in contact with animals in the last month",
            "animal_contact_frequency": "How often are they in contact with animals",
            "animal_contact_type": "Which animals have they been in contact with",
            "barefoot_around_house": "How often do they walk barefoot around the house",
            "barefoot_around_house_notes": "Notes about barefoot walking around house",
            "boil_water": "Do they boil water before consuming it",
            "boil_water_notes": "Notes about boiling water"
        }
        widgets = {
            'animal_contact_type': forms.CheckboxSelectMultiple(),
            'type_of_animal_near_water_source': forms.CheckboxSelectMultiple(),
        }


    def __init__(self, *args, **kwargs):
        if 'event' in kwargs:
            event = kwargs.pop('event')
            kwargs.update(initial={
                'event': event
            })
        super(ResidentSurveyForm, self).__init__(*args, **kwargs)
        if 'event' in kwargs:
            event_obj = Event.objects.get(id=event)
            self.fields['subject'].queryset = Subject.objects.filter(
                location=event_obj.location
            ).order_by('given_name')

