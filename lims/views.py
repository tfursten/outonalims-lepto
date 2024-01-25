import io
import pandas as pd
from django.shortcuts import render
from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, JsonResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, CreateView, DeleteView, UpdateView, DetailView)
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import ProtectedError, Count, Q, Max, Min
from import_export import resources

from ajax_datatable.views import AjaxDatatableView
from cualid import create_ids

import reportlab
from reportlab.lib.pagesizes import (LETTER, A4)
from reportlab_qrcode import QRCodeImage
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


from .models import (
    Sample, Location, Researcher, Event,
    SampleBox, Neighborhood, Subject,
    Label, Test, SampleResult, Sequencing)

from .forms import (
    LocationForm, ResearcherForm,
    EventForm, SampleForm, SampleBoxForm, NeighborhoodForm,
    SamplePrint, SubjectForm, SampleUploadFileForm,
    LabelForm, TestForm, SampleResultForm, FixIDS,
    SequenceForm, SelectEventForm)


# from difflib import get_close_matches
# Create your views here.
class SamplePermissionsMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # This will redirect to the login view
            return self.handle_no_permission()
        if not self.request.user.groups.filter(name__in=["Manager", "Staff-Lab"]).exists():
            # Redirect the user to not auth page
            return render(request, 'lims/not_authorized_error.html')
        # Checks pass, let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)
    

class SubjectPermissionsMixin(AccessMixin):
    """
    Lab staff does not have permissions to view subject information
    This mixin is placed on all subject info views and redirects
    lab staff to non authorized page.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # This will redirect to the login view
            return self.handle_no_permission()
        if not self.request.user.groups.filter(name__in=["Manager", "Staff-DataEntry"]).exists():
            # Redirect the user to not auth page
            return render(request, 'lims/not_authorized_error.html')
        # Checks pass, let http method handlers process the request
        return super().dispatch(request, *args, **kwargs)
    

def index(request):
    return render(request, 'lims/dashboard.html')

def help(request):
    return render(request, 'lims/help.html')

def search_view(request):
    code = request.GET.get('code')
    sample = Sample.objects.filter(name=code)
    if len(sample):
        return redirect('lims:sample_detail', pk=int(sample[0].id))
    else:
        return render(request, 'lims/sample_not_found.html', {'sample': code})


# ============== FIX IDS =================

def fix_cualid_function(existing_ids, check_id, thresh=0.5):
    if not check_id:
        # if there was no id to check
        return ''
    fixed_id = get_close_matches(check_id, existing_ids, 1, thresh)
    if not len(fixed_id):
        fixed_id = 'Cannot Correct ID!'
    else:
        fixed_id = fixed_id[0]
    return fixed_id


def fix_ids(request):
    form = FixIDS()
    if request.method == "POST":
        form = FixIDS(request.POST)
        if form.is_valid():
            sample_id = request.POST.get('sample_id')
            subject_id = request.POST.get('subject_id')
            existing_sample_ids = [s.name for s in Sample.objects.all()]
            existing_subject_ids = [s.subject_ui for s in Subject.objects.all()]
            fixed_sample = fix_cualid_function(existing_sample_ids, sample_id)
            fixed_subject = fix_cualid_function(existing_subject_ids, subject_id)
            return render(request, 'lims/fix_ids.html', {
                'form': form,
                'fixed_sample': fixed_sample,
                'fixed_subject': fixed_subject})
            
    return render(request, 'lims/fix_ids.html', {'form': form})


# ============== LOCATIONS ================================

class LocationListView(LoginRequiredMixin, ListView):
    template_name_suffix = "_list"
    context_object_name = 'location_list'
    model = Location

class LocationFormView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Location
    template_name_suffix = '_new'
    form_class = LocationForm
    success_message = "Location was successfully added: %(name)s"

    def get_success_url(self):
        return reverse('lims:location_detail', args=(self.object.id,))


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location

class LocationUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Location
    template_name_suffix = '_update'
    form_class = LocationForm
    success_message = "Location was successfully updated:  %(name)s"
    def get_success_url(self):
        return reverse('lims:location_detail', args=(self.object.id,))


class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    success_url = reverse_lazy('lims:location_list', args=())
    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            return render(request, "lims/protected_error.html")

# ============== NEIGHBORHOODS ================================

class NeighborhoodListView(LoginRequiredMixin, ListView):
    template_name_suffix = "_list"
    context_object_name = 'neighborhood_list'
    model = Neighborhood


class NeighborhoodFormView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Neighborhood
    template_name_suffix = '_new'
    form_class = NeighborhoodForm
    success_message = "Neighborhood was successfully added: %(name)s"

    def get_success_url(self):
        return reverse('lims:neighborhood_detail', args=(self.object.id,))


class NeighborhoodDetailView(LoginRequiredMixin, DetailView):
    model = Neighborhood

class NeighborhoodUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Neighborhood
    template_name_suffix = '_update'
    form_class = NeighborhoodForm
    success_message = "Neighborhood was successfully updated:  %(name)s"
    def get_success_url(self):
        return reverse('lims:neighborhood_detail', args=(self.object.id,))


class NeighborhoodDeleteView(LoginRequiredMixin, DeleteView):
    model = Neighborhood
    success_url = reverse_lazy('lims:neighborhood_list', args=())
    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            return render(request, "lims/protected_error.html")


# ============== RESEARCHER ================================


class ResearcherListView(LoginRequiredMixin, ListView):
    template_name_suffix = "_list"
    context_object_name = 'researcher_list'
    model = Researcher


class ResearcherFormView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Researcher
    template_name_suffix = '_new'
    form_class = ResearcherForm
    success_message = "Researcher was successfully added: %(name)s"

    def get_success_url(self):
        return reverse('lims:researcher_detail', args=(self.object.id,))

class ResearcherDetailView(LoginRequiredMixin, DetailView):
    model = Researcher


class ResearcherUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Researcher
    template_name_suffix = '_update'
    form_class = ResearcherForm
    success_message = "Researcher was successfully updated:  %(name)s"
    def get_success_url(self):
        return reverse('lims:researcher_detail', args=(self.object.id,))


class ResearcherDeleteView(LoginRequiredMixin, DeleteView):
    model = Researcher
    success_url = reverse_lazy('lims:researcher_list', args=())
    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            return render(request, "lims/protected_error.html")

# ============== EVENTS ================================
class EventListView(LoginRequiredMixin, ListView):
    template_name_suffix = "_list"
    context_object_name = 'event_list'
    model = Event


class EventFormView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Event
    template_name_suffix = '_new'
    form_class = EventForm
    success_message = "Event was successfully added: %(name)s"

    def get_success_url(self):
        return reverse('lims:event_detail', args=(self.object.id,))

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event


class EventUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Event
    template_name_suffix = '_update'
    form_class = EventForm
    success_message = "Event was successfully updated:  %(name)s"
    def get_success_url(self):
        return reverse('lims:event_detail', args=(self.object.id,))


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('lims:event_list', args=())
    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            return render(request, "lims/protected_error.html")
        

# ============== SUBJECTS ===============================
class SubjectListView(LoginRequiredMixin, ListView):
    template_name = "lims/subject_list.html"
    model = Subject
    context_object_name = 'subject_list'

    def get_queryset(self):
        return None

class SubjectFormView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Subject
    template_name_suffix = '_new'
    form_class = SubjectForm
    
    success_message = "Subject was successfully added"

    def get_success_url(self):
        return reverse('lims:subject_detail', args=(self.object.id,))


class SubjectDetailView(LoginRequiredMixin, DetailView):
    model = Subject


class SubjectUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Subject
    template_name_suffix = '_update'
    form_class = SubjectForm
    success_message = "Subject was successfully updated"
    def get_success_url(self):
        return reverse('lims:subject_detail', args=(self.object.id,))
    

class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    success_url = reverse_lazy('lims:subject_list', args=())

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            return render(request, "lims/protected_error.html")


@login_required
def subject_list_json_view(request):
    subjects = Subject.objects.select_related().values(
        'id',
        'given_name',
        'family_name',
        'location__name',
        'location__id',
        'location__neighborhood__name',
        'location__neighborhood__id',
        'consent_status',
        'birth_date',
        'sex'
        )
    data = {'data': list(subjects)}
    return JsonResponse(data, safe=False)


    

# ============== SAMPLES ================================

class SampleListView(SamplePermissionsMixin, ListView):
    template_name = "lims/sample_list.html"
    context_object_name = 'sample_list'
    model = Sample

    def get_queryset(self):
        return None
    
class SampleDetailView(SamplePermissionsMixin, DetailView):
    model = Sample
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = SampleResult.objects.filter(sample=self.kwargs['pk'])
        context['results'] = results
        return context

class SampleUpdateView(SamplePermissionsMixin, LoginRequiredMixin, UpdateView):
    model = Sample
    template_name_suffix = '_update'
    form_class = SampleForm
    success_message = "Sample was successfully updated"

    def get_success_url(self):
        return reverse('lims:sample_detail', args=(self.object.id,))
    

@login_required   
def upload_sample_file(request, pk):
    if request.method == 'POST':
        form = SampleUploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            data = pd.read_excel(
                request.FILES['file'],
                skiprows=0,
                usecols=['Sample ID', 'Subject Given Name', 'Subject Family Name', 'Event', 'Location', 'Neighborhood',
                 'Collection Status', 'Sample Type', 'Sample Source'], dtype=str)
            
            data = data.fillna("")
            data['Upload Status'] = "Success!"
            for n, row in data.iterrows():
                given_name = str(row['Subject Given Name'])
                family_name = str(row['Subject Family Name'])
                try:
                    sample = Sample.objects.get(name=row['Sample ID'])
                except Sample.DoesNotExist:
                    messages.add_message(
                        request,
                        messages.WARNING,
                        "Sample ID does not exist: {}".format(row['Sample ID']))
                    data.loc[n, 'Upload Status'] = "Sample not found!"
                    continue

                if given_name or family_name:
                    try:
                        subject = Subject.objects.get(
                            given_name=given_name if given_name else None,
                            family_name=family_name if family_name else None,
                            location=sample.collection_event.location.id)
                        sample.subject = subject
                    except Subject.MultipleObjectsReturned:
                        messages.add_message(
                            request,
                            messages.WARNING,
                            'Multiple subjects found: {0}. Please manually edit subject for this sample: {1}.'.format(
                                " ".join([n for n in [given_name, family_name] if n], sample.name)
                            ))
                        data.loc[n, 'Upload Status'] = "Subject not found!"

                    except Subject.DoesNotExist:
                        messages.add_message(
                            request,
                            messages.WARNING,
                            'Subject not found: {}. Please first add subject and resubmit.'.format(
                                " ".join([n for n in [given_name, family_name] if n])
                            ))
                        data.loc[n, 'Upload Status'] = "Subject not found!"

                if row['Collection Status']:
                    sample.collection_status = row['Collection Status']
                else:
                    sample.collection_status = None
                if row['Sample Type']:
                    sample.sample_type = row['Sample Type']
                else:
                    sample.sample_type = None
                if row['Sample Source']:
                    sample.source = row['Sample Source']
                else:
                    sample.source = None
                
                sample.save()
            data = data.to_json(orient="records")
            
            return render(
                request,
                'lims/sample_upload_complete.html',
                {'data': data})
    else:
        form = SampleUploadFileForm()
    return render(request, 'lims/sample_upload.html', {'form': form})




@login_required
def select_event_for_sample_labels(request):
    form = SelectEventForm(hide_count=True)
    if request.method == "POST":
        form = SelectEventForm(request.POST, hide_count=True)
        if form.is_valid():
            event = request.POST.get('event')
            return redirect('lims:sample_labels_options', pk=event)
    return render(request, 'lims/samples_print_labels_select_event.html', {'form': form})


@login_required
def sample_label_options(request, pk):
    form = SamplePrint(initial={
        'label_paper': 1, 'abbreviate': False,})
    event = Event.objects.get(pk=pk)
    samples = Sample.get_samples_for_event(event)
    context = {'samples': samples, 'event': event, 'form': form}
    if request.method == "POST":
        form = SamplePrint(request.POST)
        if form.is_valid():
            start_position = request.POST.get('start_position')
            label_paper = request.POST.get('label_paper')
            abbreviate = request.POST.get('abbreviate')
            reps = request.POST.get('replicates')
            selected_samples = request.POST.getlist('ids')
            return sample_labels_pdf(samples=selected_samples,
                start_position=start_position,
                label_paper=label_paper, abbreviate=abbreviate, replicates=reps,
                outfile_name="{}_sample_labels".format(event.name.replace(" ", "_")))
    return render(request, 'lims/sample_print_options.html', context)



@login_required
def add_samples(request, pk=None):
    if pk:
        form = SelectEventForm(initial = {'event': pk})
    else:
        form = SelectEventForm()
    if request.method == 'POST':
        form = SelectEventForm(request.POST)
        if form.is_valid():
            event_id = request.POST.get('event')
            additional_samples = int(request.POST.get('additional_samples'))
            event = Event.objects.get(id=event_id)
            location = event.location
            subjects = Subject.objects.filter(location__id=location.id).values_list('id', flat=True)
            existing_subj_samples = Sample.objects.filter(collection_event__id=event.id).values_list('subject', flat=True)
            create_samples_for_subjects = Subject.objects.filter(
                pk__in=list(set(subjects).difference(set(existing_subj_samples))))
            name_size = 8
            existing_ids = list(Sample.objects.all().values_list('name', flat=True))
            n_new = additional_samples + len(create_samples_for_subjects)
            new_cual_ids = [cid[0] for cid in create_ids(n_new, name_size, existing_ids=existing_ids)]
            for subj in create_samples_for_subjects:
                # create new samples for subjects that have not been added
                new_samp = Sample(
                    name=new_cual_ids.pop(),
                    subject=subj,
                    collection_event=event)
                new_samp.save(force_insert=True)
            
            for samp in range(additional_samples):
                new_samp = Sample(
                    name=new_cual_ids.pop(),
                    collection_event=event
                )
                new_samp.save(force_insert=True)


            return redirect(
                'lims:event_detail_samples',
                pk=event.id)
    return render(request, 'lims/samples_new.html', {'form':form})



class EventSampleListView(SamplePermissionsMixin, DetailView):
    template_name = "lims/event_sample_list.html"
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        samples = Sample.objects.filter(collection_event=self.kwargs['pk'])
        context['samples'] = samples
        return context

   

@login_required
def select_event_for_sample(request):
    form = SelectEventForm(hide_count=True)
    if request.method == "POST":
        form = SelectEventForm(request.POST, hide_count=True)
        if form.is_valid():
            event = request.POST.get('event')
            return redirect('lims:sample_labels_options', event_id=event)
    return render(request, 'lims/samples_print_labels_select_event.html', {'form': form})



@login_required
def sample_table_update_view(request):
    if (request.method == "POST") and (request.POST.get('action') == "edit"):
        update_values = {}
        # pull values from request
        for k, v in request.POST.items():
            if "data" in k:
                row_id = int(k.replace("[", " ").replace("]", "").split(" ")[1])
                if row_id not in update_values:
                    update_values[row_id] = {}
                if "collection_status" in k:
                    update_values[row_id]['collection_status'] = v
                elif "sample_type" in k:
                    update_values[row_id]['sample_type'] = v
                elif "source" in k:
                    update_values[row_id]['source'] = v
        # Pull objects and check if object exists
        # return if object/s don't exist without doing any update
        for object_id in update_values.keys():
            try:
                sample = Sample.objects.get(pk=object_id)
                update_values[object_id]['object'] = sample
            except Sample.DoesNotExist as e:
                return JsonResponse({"error": str(e)})
        # Form validation
        json_response = {"data": []}
        for obj_id, vals in update_values.items():
            ori_post = request.POST.copy()
            ori_post['sample'] = vals['object']
            
            for k, v in vals.items():
                if k != 'object':
                    ori_post[k] = v
            
            form = SampleForm(ori_post)

            if form.is_valid():
                data = Sample.objects.filter(pk=obj_id).values(
                    'id', 'name', 'subject__id', 'subject__given_name', 'subject__family_name',
                    'collection_event__location__neighborhood__name',
                    'collection_event__location__neighborhood__id',
                    'collection_event__name', 'collection_event__id', 'collection_event__location__name',
                    'collection_event__location__id',
                    'collection_status', 'sample_type', 'source')[0]
                data['collection_status'] = vals['collection_status']
                data['sample_type'] = vals['sample_type']
                data['source'] = vals['source']

                json_response['data'].append(data)
            else:
                return JsonResponse({"error": str(form.errors)})
        # Update database
        for obj_id, vals in update_values.items():
            sample = vals['object']
            sample.collection_status = vals['collection_status']
            sample.sample_type = vals['sample_type']
            sample.source = vals['source']
            sample.save()
        return JsonResponse(json_response)


    
@login_required
def sample_list_json_view(request):
    samples = Sample.objects.all().values(
        'id', 'name', 'subject__id', 'subject__given_name', 'subject__family_name',
        'collection_event__location__neighborhood__name',
        'collection_event__location__neighborhood__id',
        'collection_event__name', 'collection_event__id', 'collection_event__location__name',
        'collection_event__location__id',
        'collection_status', 'sample_type', 'source'
        )
    data = {'data': list(samples)}
    return JsonResponse(data, safe=False)


# ============== SAMPLE RESULTS ================================

class SampleResultListView(SamplePermissionsMixin, ListView):
    template_name_suffix = "_list"
    context_object_name = 'result_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sample_results = SampleResult.objects.all().values(
        'id', 'sample__collection_event__name', 'sample__collection_event__id',
        'sample__location__id', 'sample__location__name',
        'test__name', 'test__id', 'sample__id', 'sample__name',
        'sample__sample_type', 'replicate', 'result', 'value',
        'notes', 'created_on')

        context['data'] = json.dumps(
            list(sample_results), cls=DjangoJSONEncoder)
        return context

    def get_queryset(self):
        """
        Return all results
        """
        return SampleResult.objects.all()
    
class SampleResultFormView(SuccessMessageMixin, SamplePermissionsMixin, CreateView):
    model = SampleResult
    template_name_suffix = '_new'
    form_class = SampleResultForm
    success_message = "Sample result was successfully added"

    def get_success_url(self):
        return reverse('lims:sample_result_detail', args=(self.object.id,))
    

class SampleResultSampleFormView(SuccessMessageMixin, SamplePermissionsMixin, CreateView):
    model = SampleResult
    template_name_suffix = '_sample_new'
    form_class = SampleResultForm
    success_message = "Sample result was successfully added"

    def get_success_url(self):
        return reverse('lims:sample_result_detail', args=(self.object.id,))

    def get_form_kwargs(self):
        kwargs = super(SampleResultSampleFormView, self).get_form_kwargs()
        kwargs['sample'] = self.kwargs['pk']
        return kwargs
    
    def get_success_url(self):
        return reverse('lims:sample_result_detail', args=(self.object.id,))
        

@login_required
def sample_excel_sheet(request, pk):
    event = Event.objects.get(id=pk)
    samples = Sample.get_samples_for_event(pk)
    sample_data = samples.values_list(
        'name', 'subject__given_name',
        'subject__family_name', 'collection_event__name',
        'collection_event__location__name', 'collection_event__location__neighborhood__name',
        'collection_status', 'sample_type', 'source')
    df = pd.DataFrame(
        sample_data, columns=['Sample ID', 'Subject Given Name', 'Subject Family Name', 'Event', 'Location', 'Neighborhood',
                 'Collection Status', 'Sample Type', 'Sample Source']
        )
    bio = io.BytesIO()
    writer = pd.ExcelWriter(bio, engine='xlsxwriter') 
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']

    n = df.shape[0]
    #Adding the header and Datavalidation list
    worksheet.data_validation('G2:G{}'.format(n + 1), {'validate': 'list', 'ignore_blank': False,
                                    'source': ['Collected','Refused','Pending','Not Collected']})
    worksheet.data_validation('H2:H{}'.format(n + 1), {'validate': 'list', 'ignore_blank': False,
                                    'source': ['Urine', 'Soil', 'Trap', 'Carcass']})
    worksheet.data_validation('I2:I{}'.format(n + 1), {'validate': 'list', 'ignore_blank': False,
                                    'source': ['Human', 'Dog', 'Cat', 'Rat', 'Mouse', 'Horse', 'Cow', 'Donkey', 'Pig', 'Environment']})
    # Create some cell formats with protection properties.
    unlocked = workbook.add_format({'locked': False})
    locked   = workbook.add_format({'locked': True})

    # Format the worksheet to unlock all cells.
    worksheet.set_column('B2:B{}'.format(n + 1), None, unlocked)
    worksheet.set_column('C2:C{}'.format(n + 1), None, unlocked)
    worksheet.set_column('G2:G{}'.format(n + 1), None, unlocked)
    worksheet.set_column('H2:G{}'.format(n + 1), None, unlocked)
    worksheet.set_column('I2:G{}'.format(n + 1), None, unlocked)

    # Turn worksheet protection on.
    worksheet.protect()
    
    
    writer.close()
    bio.seek(0)
    return FileResponse(
        bio, as_attachment=True,
        filename="./EventSamples-{}.xlsx".format(slugify(event.name)))



# ============== SAMPLE BOXES ================================
class SampleBoxListView(LoginRequiredMixin, ListView):
    template_name_suffix = "_list"
    context_object_name = 'box_list'

    def get_queryset(self):
        """
        Return all boxes
        """
        return SampleBox.objects.all()
    

# ============== LABELS =================================

class LabelListView(LoginRequiredMixin, ListView):
    template_name_suffix = "_list"
    context_object_name = 'label_list'

    def get_queryset(self):
        """
        Return all labels
        """
        return Label.objects.all()


class LabelFormView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Label
    template_name_suffix = '_new'
    form_class = LabelForm
    success_message = "Label format was successfully added: %(name)s"


    def get_success_url(self):
        return reverse('lims:label_detail', args=(self.object.id,))
        

class LabelDetailView(LoginRequiredMixin, DetailView):
    model = Label


class LabelUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Label
    template_name_suffix = '_update'
    form_class = LabelForm
    success_message = "Label format was successfully updated:  %(name)s"
    
    def get_success_url(self):
        return reverse('lims:label_detail', args=(self.object.id,))

class LabelDeleteView(LoginRequiredMixin, DeleteView):
    model = Label
    success_url = reverse_lazy('lims:label_list', args=())
    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            return render(request, "lims/protected_error.html")
        


def get_x_y_coordinates(
        columns, rows, left_margin, top_margin,
        label_width, label_height, row_margin, col_margin ):
    x = label_width + col_margin
    y = -(label_height + row_margin)
    for column in range(int(columns)):
        for row in range(int(rows)):
            x_coord = left_margin + (x * column)
            y_coord = top_margin + (y * row)
            yield (x_coord * mm, y_coord * mm)


def sample_labels_pdf(
    samples, start_position,
    label_paper, abbreviate, replicates, outfile_name):
    """
    Use Cual-id code to generate labels with barcodes
    """
    # Create a file-like buffer to receive PDF data.
    
    label = Label.objects.get(pk=label_paper)
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    paper_size = {'LETTER': LETTER, 'A4': A4}
    barcode_canvas = canvas.Canvas(buffer, pagesize=paper_size[label.paper_size])
    page_width, page_height = paper_size[label.paper_size]
    columns=label.columns
    rows=label.rows
    x_start=label.left_margin
    y_start=(page_height / mm) - (label.top_margin)
    xy_coords = list(get_x_y_coordinates(
        columns, rows, x_start, y_start,
        label.label_width, label.label_height,
        label.row_margin, label.col_margin))
    c = int(start_position) - 1
    for sample in Sample.objects.filter(pk__in=samples).order_by('name').select_related():
        for rep in range(int(replicates)):
            x = xy_coords[c][0] + (label.left_padding * mm)
            y = xy_coords[c][1] - (label.top_padding * mm)
            qr_size = label.qr_size
            qr_code = QRCodeImage(sample.name, size=qr_size * mm)
            qr_code.drawOn(barcode_canvas, x , y - ((qr_size - 4) * mm))
            barcode_canvas.setFont("Helvetica", label.font_size)
            # Add line for last name and first name, cuts off last name before max_chars so that some characters
            # from first name will be included if full name does not fit.
            if abbreviate == "on":
                sample_type = sample.sample_type if sample.sample_type else ""
                source = sample.source if sample.source else ""
                barcode_canvas.drawString(x + (qr_size * mm), y, "{0}".format(sample.name))
                barcode_canvas.drawString(x + (qr_size * mm), (y - (label.line_spacing * mm)), "{0}".format(sample_type))
                barcode_canvas.drawString(x + (qr_size * mm), (y - ((label.line_spacing * 2) * mm)), "{0}".format(source))

            else:
                if sample.subject:
                    given = sample.subject.given_name if sample.subject.given_name else ""
                    family = sample.subject.family_name if sample.subject.family_name else ""
                    barcode_canvas.drawString(x + (qr_size * mm), y, " ".join([given, family])[:label.max_chars])
                else:
                    barcode_canvas.drawString(x + (qr_size * mm), y, "Name:" + "_" * (label.max_chars - 5))
                sample_type = sample.sample_type if sample.sample_type else "Type:_______"
                source = sample.source if sample.source else "Source:_________"
                barcode_canvas.drawString(x + (qr_size * mm), (y - (label.line_spacing * mm)), "{0} {1}".format(sample_type, source)[:label.max_chars])
                event_name = sample.collection_event.name
                location = sample.collection_event.location.name
                barcode_canvas.drawString(
                    x + (qr_size * mm), (y - ((label.line_spacing * 2) * mm)), "{0} {1} {2}".format(sample.name, event_name, location)[:label.max_chars])
            if c < ((rows*columns) - 1):
                c += 1
            else:
                c = 0
                barcode_canvas.showPage()

    # Close the PDF object cleanly, and we're done.
    barcode_canvas.showPage()
    barcode_canvas.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(
        buffer, as_attachment=True,
        filename="{}.pdf".format(outfile_name))
    
# ============== TESTS =================================

class TestListView(LoginRequiredMixin, ListView):
    template_name_suffix = "_list"
    context_object_name = 'test_list'

    def get_queryset(self):
        """
        Return all tests
        """
        return Test.objects.all()
    


# ============== SEQUENCING =================================

class SequenceListView(LoginRequiredMixin, ListView):
    template_name_suffix = "_list"
    context_object_name = 'sequence_list'

    def get_queryset(self):
        """
        Return all tests
        """
        return Sequencing.objects.all()