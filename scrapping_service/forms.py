from django import forms

class JobOffersForm(forms.Form):
    query = forms.CharField(label='Keyword query', max_length=100)
    limit = forms.IntegerField(label='Max results', min_value=1, max_value=100, initial=10)
    delay = forms.IntegerField(label='Delay (seconds)', min_value=0, max_value=10, initial=0)

class OfferFilterForm(forms.Form):
    location = forms.CharField(required=False, initial='')
    contract_type = forms.CharField(required=False, initial='')
    salary_min = forms.IntegerField(required=False)
    salary_max = forms.IntegerField(required=False)
    SENIORITY_CHOICES = [
        ('', 'Choose a level of seniority'),
        ('Junior', 'Junior'),
        ('Mid', 'Mid'),
        ('senior', 'Senior'),
        ('Odpowiednie doświadczenie zawodowe', 'Odpowiednie doświadczenie zawodowe'),
        ('Doświadczenie nie jest wymagane', 'Doświadczenie nie jest wymagane')
    ]
    
    seniority = forms.ChoiceField(
        choices=SENIORITY_CHOICES,
        required=False,
        initial='',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
