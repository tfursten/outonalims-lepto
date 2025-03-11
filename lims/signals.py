from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Test, SampleResult



@receiver(post_save, sender=Test)
def update_sample_results(sender, instance, **kwargs):
    """
    Updates all SampleResult objects linked to this Test instance whenever the threshold changes.
    If 'value' is set, it updates 'result' to 'Positive' or 'Negative'. Otherwise, no changes are made.
    """
    sample_results = instance.sampleresult_set.all()
    
    for result in sample_results:
        # Only update if 'value' is set (not None or empty)
        if result.value is not None:
            result.result = "Positive" if result.value <= instance.threshold else "Negative"
            result.save()




@receiver(pre_save, sender=SampleResult)
def update_result_status(sender, instance, **kwargs):
    """
    Updates the 'result' status:
    - On initial creation, it sets 'result' based on 'value'.
    - If 'value' is None, 'result' is set to 'Pending'.
    - If 'value' is updated later, 'result' is updated accordingly.
    """
    
    if instance.pk:  # Check if the instance already exists (update case)
        try:
            old_instance = SampleResult.objects.get(pk=instance.pk)
            if old_instance.value != instance.value:  # Only update if 'value' has changed
                if instance.value is None:
                    instance.result = "Pending"
                else:
                    instance.result = "Positive" if float(instance.value) <= instance.test.threshold else "Negative"
        except SampleResult.DoesNotExist:
            pass  # Allow normal creation
    else:  # This is a new record (initial save)
        if instance.value is not None:
            instance.result = "Positive" if float(instance.value) <= instance.test.threshold else "Negative"
