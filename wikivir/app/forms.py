from django.forms import ModelForm
from .models import MalwareSample

class MalwareSampleForm(ModelForm):
    class Meta:
        model = MalwareSample
        fields = ('file',)
        #fields = ('fileHash', 'filePath', 'file',)

    def save(self, commit=True):
        inst = super(MalwareSampleForm, self).save(commit=False)
        if commit:
            inst.save()
        return inst
