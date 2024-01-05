import datetime
import json
from django import forms
from django.forms import ModelForm, CheckboxInput, SelectMultiple
from .models import (
    Sample, Location, Researcher,
    Event, SampleBox, Neighborhood,
    Label, SampleResult, Subject,
    Test, Sequencing)
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
        fields = ['subject', 'collection_status', 'sample_type', 'source', 'notes']

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
    subject_id = forms.CharField(
        label="Subject ID", max_length=10,
        help_text="Enter subject ID to correct", required=False)


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
        fields = ['name', 'protocol', 'detects']

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
        fields = ['sample', 'test', 'replicate', 'result', 'value', 'notes', 'researcher']
    def __init__(self, *args, **kwargs):
            if 'sample' in kwargs:
                sample = kwargs.pop('sample')
                kwargs.update(initial={
                    'sample': sample
                })
            super(SampleResultForm, self).__init__(*args, **kwargs)
            self.fields['sample'].queryset = Sample.objects.filter(
                collection_status="Collected").order_by('name')
        
