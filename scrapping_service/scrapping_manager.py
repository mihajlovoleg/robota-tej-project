from bs4 import BeautifulSoup
import requests
import time
import re

def extract_numbers_from_salary(salary):

    if not salary:
        return None
    
    numbers = re.findall(r'\d+', salary)

    
    numbers = [num.replace(" ", "") for num in numbers]
    if len(numbers) == 1:
        return [int(numbers[0])]
    elif len(numbers) == 2 and 'godz' in salary:
        return [float(str(numbers[0])+'.'+str(numbers[1]))]
    elif len(numbers) == 2:
        return [int(str(numbers[0])+str(numbers[1]))]
    elif len(numbers) == 4:
        return [int(str(numbers[0])+str(numbers[1])), int(str(numbers[2])+str(numbers[3]))]

def check_seniority(seniority):
    if not seniority:
        return None
    
    if 'Mid' in seniority:
        return 'Mid'
    elif 'Junior' in seniority:
        return 'Junior'
    elif 'Senior' in seniority:
        return 'Senior'
    

    

class PracujPlScraperService:
    def __init__(self, q):
        self.base_url = 'https://www.pracuj.pl/praca/'
        self.q = q

    def get_job_links(self):
        query_words = self.q.split()
        query = '%20'.join(query_words)
        url = self.base_url + query + ';kw'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        job_cards = soup.find_all('a')
        return [
            job_card['href'] for job_card in job_cards
            if 'href' in job_card.attrs and re.match(r'^https://www\.pracuj\.pl/praca/', job_card['href'])
        ]

    def scrape_job_details(self, link):
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'lxml')

        offer_title = soup.find('h1', {'data-scroll-id': 'job-title'}).text if soup.find('h1', {'data-scroll-id': 'job-title'}) else None
        firm_name = soup.find('h2', {'data-scroll-id': 'employer-name'}).text.strip() if soup.find('h2', {'data-scroll-id': 'employer-name'}) else None
        firm_name = re.sub(r'(O firmie|About the company)', '', firm_name).strip() if firm_name else None
        offer_location = soup.find('div', {'data-test': 'offer-badge-description'}).text.strip() if soup.find('div', {'data-test': 'offer-badge-description'}) else None
        contract_kind = soup.find('li', {'data-test': 'sections-benefit-contracts'}).text.strip() if soup.find('li', {'data-test': 'sections-benefit-contracts'}) else None
        salary = soup.find('div', {'data-test': 'text-earningAmount'}).text.strip() if soup.find('div', {'data-test': 'text-earningAmount'}) else None
        employment_type = soup.find('li', {'data-scroll-id': 'work-modes'}).text.strip() if soup.find('li', {'data-scroll-id': 'work-modes'}) else None
        min_salary, max_salary = None, None
        
        
        if salary:
            if len(extract_numbers_from_salary(salary)) == 1:

                min_salary, max_salary = extract_numbers_from_salary(salary)[0], extract_numbers_from_salary(salary)[0]
            elif salary and len(extract_numbers_from_salary(salary)) == 2:
                min_salary, max_salary = extract_numbers_from_salary(salary)[0], extract_numbers_from_salary(salary)[1]

        seniority_li = soup.find('li', {'data-scroll-id': 'position-levels'})
        seniority = None
        if seniority_li:
            seniority_div = seniority_li.find('div', {'class': 't1g3wgsd'})
            if seniority_div:
                seniority = check_seniority(seniority_div.text.strip())

        return {
            'job_title': offer_title,
            'company_name': firm_name,
            'location': offer_location,
            'contract_type': contract_kind,
            'min_salary':min_salary,
            'max_salary':max_salary,
            'employment_type': employment_type,
            'url': link,
            'seniority': seniority
        }

    def scrape_jobs(self, limit, delay):
        job_links = self.get_job_links()[:limit]
        job_data = []
        existing_urls = set()  
        for link in job_links:
            job_details = self.scrape_job_details(link)
            if job_details and job_details['url'] not in existing_urls:  
                job_data.append(job_details)
                existing_urls.add(job_details['url'])  
            time.sleep(delay)
        return job_data


class OlxScraperService:
    def __init__(self, q):
        self.base_url = 'https://www.olx.pl/praca/informatyka/'
        self.q = q

    def get_job_links(self):
        query_words = self.q.split()
        query = '-'.join(query_words)
        url = self.base_url + 'q-' + query
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        job_cards = soup.find_all('a')
        return [
            'https://olx.pl' + job_card['href'] for job_card in job_cards
            if 'href' in job_card.attrs and re.match(r'^/oferta/praca/', job_card['href'])
        ]
    
    def scrape_job_details(self, link):
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'lxml')

        offer_title = soup.find('h1', {'class': 'css-16yqzuf'})
        offer_title = offer_title.text.strip() if offer_title else None

        firm_name = soup.find('p', {'class': 'css-9pgvpt'})
        firm_name = firm_name.text.strip() if firm_name else None

        offer_location = soup.find('span', {'class': 'css-d5w927'})
        offer_location = offer_location.text.strip() if offer_location else None

        contract_kind_elem = soup.find('p', {'class': 'css-15qhxrj'})
        contract_kind = contract_kind_elem.text.strip() if contract_kind_elem and re.search(r'\bUmowa\b', contract_kind_elem.text, re.IGNORECASE) else None

        salary_elem = soup.find('p', {'class': 'css-e2x4k9'})
        salary = salary_elem.text.strip() if salary_elem else None

        employment_elem = soup.find('p', {'class': 'css-1pq6o0q'})
        employment_type = employment_elem.text.strip() if employment_elem and re.search(r'\bMiejsce pracy\b', employment_elem.text, re.IGNORECASE) else None
        min_salary, max_salary = None, None
        
        if salary:
            if len(extract_numbers_from_salary(salary)) == 1:

                min_salary, max_salary = extract_numbers_from_salary(salary)[0], extract_numbers_from_salary(salary)[0]
            elif salary and len(extract_numbers_from_salary(salary)) == 3:
                min_salary, max_salary = extract_numbers_from_salary(salary)[0], extract_numbers_from_salary(salary)[1]
        seniority_elems = soup.find_all('span', {'class':'css-1pq6o0q'})
        seniority = None
        for seniority_elem in seniority_elems:
            if re.search(r'doświadczenie', seniority_elem.text, re.IGNORECASE):
                seniority = seniority_elem.text.strip()
                break
        return {
            'job_title': offer_title,
            'company_name': firm_name,
            'location': offer_location,
            'contract_type': contract_kind,
            'min_salary':min_salary,
            'max_salary':max_salary,
            'employment_type': employment_type,
            'url': link,
            'seniority': seniority
        }

    def scrape_jobs(self, limit, delay):
        job_links = self.get_job_links()[:limit]
        job_data = []
        existing_urls = set()
        for link in job_links:
            job_details = self.scrape_job_details(link)
            if job_details and job_details['url'] not in existing_urls:
                job_data.append(job_details)
                existing_urls.add(job_details['url'])
            time.sleep(delay)
        return job_data
    

class JustJoinItScraperService:
    def __init__(self, q):
        self.base_url = 'https://justjoin.it'
        self.q = q

    def get_job_links(self):
        query_words = self.q.split()
        query = '%20'.join(query_words)
        url = self.base_url + '/job-offers/all-locations' + '?keyword='+ query
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        offer_cards = soup.find_all('a')
        return [
            self.base_url + offer_card['href'] for offer_card in offer_cards
            if 'href' in offer_card.attrs and re.match(r'^/job-offer/', offer_card['href'])
        ]

    def scrape_job_details(self, link):
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'lxml')

        offer_title_div = soup.find('div', {'class': 'MuiBox-root css-s52zl1'})

        offer_title = offer_title_div.find('h1').text.strip() if offer_title_div and offer_title_div.find('h1') else None

        firm_name = offer_title_div.find('a').text.strip() if offer_title_div and offer_title_div.find('a') else None

        offer_location = soup.find('span', {'class': 'css-1o4wo1x'})
        offer_location = offer_location.text.strip() if offer_location else None

        salary_elem = soup.find('span', {'class': 'css-1pavfqb'})
        
        min_salary, max_salary = None, None
        
        if salary_elem:
            salary_parts = salary_elem.text.split(' - ')
            salary = f"{salary_parts[0].strip()} - {salary_parts[1].strip()}" if len(salary_parts) > 1 else salary_parts[0].strip()
            
            if len(extract_numbers_from_salary(salary)) == 1:
                salary_numbers = extract_numbers_from_salary(salary)
                min_salary, max_salary = salary_numbers[0], salary_numbers[0]
            elif len(extract_numbers_from_salary(salary)) == 2:
                min_salary, max_salary = extract_numbers_from_salary(salary)[0], extract_numbers_from_salary(salary)[1]
            
        else:
            min_salary, max_salary = None

        all_employment_divs = soup.find_all('div', {'class': 'MuiBox-root css-if24yw'})

        contract_kind = None
        seniority = None

        for div in all_employment_divs:
            
            label_div = div.find('div', {'class': 'MuiBox-root css-1k7fv8q'})  
            value_div = div.find('div', {'class': 'MuiBox-root css-ktfb40'})

            if label_div and value_div:
                
                label_text = label_div.text.strip()
                value_text = value_div.text.strip()

                if "Employment Type" in label_text:
                    contract_kind = value_text
                
                elif "Experience" in label_text:
                    seniority = check_seniority(value_text)
                    break





        return {
            'job_title': offer_title,
            'company_name': firm_name,
            'location': offer_location,
            'contract_type': contract_kind,
            'min_salary':min_salary,
            'max_salary':max_salary,
            'employment_type':None,
            'url': link,
            'seniority':seniority
        }

    def scrape_jobs(self, limit, delay):
        job_links = self.get_job_links()[:limit]
        job_data = []
        existing_urls = set()
        for link in job_links:
            job_details = self.scrape_job_details(link)
            if job_details and job_details['url'] not in existing_urls:
                job_data.append(job_details)
                existing_urls.add(job_details['url'])
            time.sleep(delay)
        return job_data


