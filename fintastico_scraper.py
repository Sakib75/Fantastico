import requests
import json
from  bs4 import BeautifulSoup
import re
from openpyxl import Workbook

# Creating .xlsx file

wb = Workbook()
file_path = "./fintastico_data.xlsx"
wb.save(file_path)

sheet = wb.active

sheet['A1'] = 'ID'
sheet['B1'] = 'COMPANY_NAME'
sheet['C1'] = 'COMPANY_LOGO'
sheet['D1'] = 'BRIEF_DESCRIPTION'
sheet['E1'] = 'DESCRIPTION'
sheet['F1'] = 'CATEGORIES'
sheet['G1'] = 'WEBSITE_URL'
sheet['H1'] = 'LINKEDIN_URL'
sheet['I1'] = 'FACEBOOK_URL'
sheet['J1'] = 'TWITTER_URL'
sheet['K1'] = 'RELATED_COMPANIES'
sheet['L1'] = 'IMAGE'
sheet['M1'] = 'SOURCE'

wb.save(file_path)



# Get all categories

def GetCategories():
	homepage = 'https://www.fintastico.com/'
	initial_response = requests.get(homepage)

	category_soup = BeautifulSoup(initial_response.text,'html.parser')

	menu = category_soup.select('.mini')[-1].select('a')

	caterories = []


	for c in menu:
		link = c['href']
		caterories.append(re.match('/services/(.*)/',link).group(1))


	return caterories

all_categories = GetCategories()


headers = {
	'x-requested-with':'XMLHttpRequest',
	'x-csrftoken':'46Gm9LiqQhMEcczXbPRzyWyNSDqkXIAermBmgByigW4iky2zsuVpKE1kUHJih5XO',
	'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Mobile Safari/537.36',
	'sec-fetch-site':'same-origin',
	'sec-fetch-mode':'cors',
	'sec-fetch-dest':'empty',
	'referer':'https://www.fintastico.com/services/banking/',
	'pragma':'no-cache',
	'cookie':"__smVID=363884d63781626ffa5e67f7b2e564febd33d3ebe5f18dd49e0c138de4b75d3e; csrftoken=46Gm9LiqQhMEcczXbPRzyWyNSDqkXIAermBmgByigW4iky2zsuVpKE1kUHJih5XO; _ga=GA1.2.1522200034.1601051067; _gid=GA1.2.146830367.1601051067; sessionid=dv07kceex6vagog4761s5dxyvedo6bsr; _fbp=fb.1.1601051068492.155304487; __smToken=q5vPY7q31hJMPc7VdSqOtZpm; _gat=1; mp_ffb52f340c0f5c04e1425ce53e56a44a_mixpanel=%7B%22distinct_id%22%3A%20%22174c61485f88e4-0e867b3734b456-333376b-1fa400-174c61485f9806%22%2C%22%24device_id%22%3A%20%22174c61485f88e4-0e867b3734b456-333376b-1fa400-174c61485f9806%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%7D",
	'cache-control':'no-cache',
	'accept-language':'en-US,en;q=0.9',
	'accept-encoding':'gzip, deflate, br',
	'accept':'*/*'
}

# Extract data from each company page

def inner_page(source_url):

	_r = requests.get(source_url)

	css_logo = '.col-xl-12 img'
	css_brief_description = ".text-dark2"
	css_web = '.web'
	css_twitter = '.tw'
	css_linkedin = '.in'
	css_facebook = '.fb'
	css_related = '.related div h4'
	css_description = '.social-links+ p'
	css_image = '.carousel img'

	soup = BeautifulSoup(_r.text,'html.parser')

	try:
		logo = soup.select(css_logo)[0]['src']

	except:
		logo = 'NULL'


	try:
		brief_description = soup.select(css_brief_description)[0].get_text()

	except:
		brief_description = 'NULL'


	try:
		website_url = soup.select(css_web)[0]['href']

	except:
		website_url = 'NULL'


	try:
		twitter_url = soup.select(css_twitter)[0]['href']

	except:
		twitter_url = 'NULL'


	try:
		linkedin_url = soup.select(css_linkedin)[0]['href']

	except:
		linkedin_url = 'NULL'


	try:
		facebook_url = soup.select(css_facebook)[0]['href']

	except:
		facebook_url = 'NULL'


	try:
		all_related_companies = ''
		related_companies = soup.select(css_related)
		for companies in related_companies:
			all_related_companies = all_related_companies + companies.get_text() + '; '

	except:
		related_companies = 'NULL'

		
	try:
		description = soup.select(css_description)[0].get_text()
	
	except:
		description = 'NULL'


	try:
		image = soup.select(css_image)[0]['src']

	except:
		image = 'NULL'

	second_data = {
	'company_logo':logo,
	'brief_description':brief_description,
	'description':description,
	'website_url':website_url,
	'linkedin_url':linkedin_url,
	'facebook_url':facebook_url,
	'twitter_url':twitter_url,
	'related_companies':all_related_companies,
	'image':image,
	
	}
	

	return second_data



all_data = []
id = 0
for cat in all_categories:
	endpage = False


	page_no = 1
	while endpage == False:
		url = f'https://www.fintastico.com/services/{cat}/?order_by=update_time&markets=&customer_type=&page={page_no}'



		r = requests.get(url,headers= headers)


		try:
			resp = json.loads(r.text)
			items = resp["items"]

			for item in items:
		
				item_url = 'https://www.fintastico.com' + item['object_url']

				# First set of data

				data_1 = {
				'id':id,
				'company_name':item['title'],
				'description':item['description'],
				'catergory':cat,
				'source':item_url,
				}
		
				
				# Second set of data

				try:

					data_2 = inner_page(item_url)
				except:
					data_2 = {}

				total_data = {**data_1,**data_2}

				# Saving data to .xlsx file

				sheet.append((id,total_data['company_name'],total_data['company_logo'],total_data['brief_description'],total_data['description'],total_data['catergory'],total_data['website_url'],total_data['linkedin_url'],total_data['facebook_url'],total_data['twitter_url'],total_data['related_companies'],total_data['image'],total_data['source']))
				wb.save(file_path)
				print(total_data)
				all_data.append(total_data)
				id = id + 1
			page_no = page_no + 1
		except:
			endpage = True
			print('end of page')
			










