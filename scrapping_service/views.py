from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .models import Offer
from django.db.models import Q
from .scrapping_manager import PracujPlScraperService, OlxScraperService, JustJoinItScraperService
from .forms import JobOffersForm, OfferFilterForm

class HomePageView(View):
    def get(self, request, *args, **kwargs):
        
        offers = Offer.objects.all()

        
        form = OfferFilterForm(request.GET)

        
        if form.is_valid():
            location = form.cleaned_data.get('location')
            contract_type = form.cleaned_data.get('contract_type')
            salary_min = form.cleaned_data.get('salary_min')
            salary_max = form.cleaned_data.get('salary_max')
            seniority = form.cleaned_data.get('seniority')

            if location:
                offers = offers.filter(location__icontains=location)

            if contract_type:
                offers = offers.filter(contract_type__icontains=contract_type)

            
            if salary_min is not None:
                offers = offers.filter(
                    Q(min_salary__gte=salary_min) |
                    Q(max_salary__gte=salary_min)  
                )

            
            if salary_max is not None:
                offers = offers.filter(
                    Q(max_salary__lte=salary_max) |
                    Q(min_salary__lte=salary_max)  
                )
            if seniority:
                offers = offers.filter(seniority__icontains=seniority)

        return render(request, 'index.html', {'offers': offers, 'form': form})

    

class AddOfferView(View):
    def get(self, request, *args, **kwargs):
        form = JobOffersForm()
        return render(request, 'add_offer.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = JobOffersForm(request.POST)
        if form.is_valid():
            
            query = form.cleaned_data['query']
            limit = form.cleaned_data['limit']
            delay = form.cleaned_data['delay']

            
            pracuj_parser = PracujPlScraperService(query)
            olx_parser = OlxScraperService(query)
            justjoin_parser = JustJoinItScraperService(query)

            
            pracuj_offers = pracuj_parser.scrape_jobs(limit, delay)
            olx_offers = olx_parser.scrape_jobs(limit, delay)
            justjoin_offers = justjoin_parser.scrape_jobs(limit, delay)

            
            all_offers = pracuj_offers + olx_offers + justjoin_offers
            unique_offers = {offer['url']: offer for offer in all_offers}.values()

            for offer in unique_offers:
                Offer.objects.create(
                    offer_title=offer['job_title'],
                    company_name=offer['company_name'],
                    location=offer['location'],
                    contract_type=offer['contract_type'],
                    min_salary=offer['min_salary'],
                    max_salary=offer['max_salary'],
                    employment_type=offer['employment_type'],
                    link=offer['url'],
                    seniority=offer['seniority']
                )

            
            return JsonResponse({'message': 'Офер успішно додано.'})

        
        return JsonResponse({'error': 'Форма невалідна.'}, status=400)
