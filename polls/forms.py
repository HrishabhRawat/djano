from django import forms
from django.forms import inlineformset_factory
from .models import Question , Choice

# A standard Model form for the Question text
class QuestionForm (forms.ModelForm):
    class Meta:
        model = Question
        fields = ["question_text"]
    
ChoiceFormSet = inlineformset_factory(
    Question, 
    Choice,
    fields = ["choice_text"],
    extra= 3,
    can_delete=True

)
