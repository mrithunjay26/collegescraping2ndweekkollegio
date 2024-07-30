from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
from bs4 import BeautifulSoup
import requests


def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)


def click_show_more(driver, num_clicks):
    try:
        for _ in range(num_clicks):
            show_more_btn = driver.find_element(By.XPATH, "//button[@data-testid='cs-show-more-results']")
            if show_more_btn.is_displayed() and show_more_btn.is_enabled():
                driver.execute_script("arguments[0].click();", show_more_btn)
                print(f"Clicked 'Show More Colleges' button {_ + 1} time(s)")
                time.sleep(3)
            else:
                print("Button not clickable or visible")
                break
    except Exception as e:
        print(f'Error clicking button: {e}')


def extract_data(soup, section):
    data = {}
    if section == 'admissions':
        data['Acceptance Rate'] = soup.find(string='Acceptance Rate').find_next().text if soup.find(
            string='Acceptance Rate') else ''
        data['Regular Application Due'] = soup.find(string='Regular Application Due').find_next().text if soup.find(
            string='Regular Application Due') else ''
        data['SAT Range'] = soup.find(string='SAT Range').find_next().text if soup.find(string='SAT Range') else ''
        data['ACT Range'] = soup.find(string='ACT Range').find_next().text if soup.find(string='ACT Range') else ''
        data['High School GPA'] = soup.find(string='High School GPA').find_next().text if soup.find(
            string='High School GPA') else ''
        data['High School Rank'] = soup.find(string='High School Rank').find_next().text if soup.find(
            string='High School Rank') else ''
        data['SAT/ACT Scores'] = soup.find(string='SAT/ACT Scores').find_next().text if soup.find(
            string='SAT/ACT Scores') else ''
        data['Recommendations'] = soup.find(string='Recommendations').find_next().text if soup.find(
            string='Recommendations') else ''
        data['Application Fee'] = soup.find(string='Application Fee').find_next().text if soup.find(
            string='Application Fee') else ''
        data['Application Types Accepted'] = soup.find(
            string='Application Types Accepted').find_next().text if soup.find(
            string='Application Types Accepted') else ''
    elif section == 'academics':
        data['Graduation Rate'] = soup.find(string='Graduation Rate').find_next().text if soup.find(
            string='Graduation Rate') else ''
        data['Majors Available'] = soup.find(string='Majors Available').find_next().text if soup.find(
            string='Majors Available') else ''
        data['Student to Faculty Ratio'] = soup.find(string='Student to Faculty Ratio').find_next().text if soup.find(
            string='Student to Faculty Ratio') else ''
        data['Retention Rate'] = soup.find(string='Retention Rate').find_next().text if soup.find(
            string='Retention Rate') else ''
        data['Majors and Degrees'] = soup.find(string='Majors and Degrees').find_next().text if soup.find(
            string='Majors and Degrees') else ''
    elif section == 'campus-life':
        data['Setting'] = soup.find(string='Setting').find_next().text if soup.find(string='Setting') else ''
        data['Undergraduate Students'] = soup.find(string='Undergraduate Students').find_next().text if soup.find(
            string='Undergraduate Students') else ''
        data['Average per Year for Campus Housing'] = soup.find(
            string='Average per Year for Campus Housing').find_next().text if soup.find(
            string='Average per Year for Campus Housing') else ''
        data['Sports'] = soup.find(string='Sports').find_next().text if soup.find(string='Sports') else ''
        data['First Years in College Housing'] = soup.find(
            string='First Years in College Housing').find_next().text if soup.find(
            string='First Years in College Housing') else ''
        data['Housing Options'] = soup.find(string='Housing Options').find_next().text if soup.find(
            string='Housing Options') else ''
        data['Activities'] = soup.find(string='Activities').find_next().text if soup.find(string='Activities') else ''
        data['Student Body'] = soup.find(string='Student Body').find_next().text if soup.find(
            string='Student Body') else ''
    return data


def scrape_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        college_name = url.split('/')[-1].replace('-', ' ').title()

        data = {
            'College Name': college_name,
            'URL': url,
        }

        sections = ['admissions', 'academics', 'campus-life']
        for section in sections:
            section_url = f"{url}/{section}"
            section_response = requests.get(section_url)
            section_response.raise_for_status()
            section_soup = BeautifulSoup(section_response.content, 'html.parser')
            section_data = extract_data(section_soup, section)
            data.update(section_data)

        return data
    except requests.RequestException as req_err:
        print(f'Request error occurred accessing URL {url}: {req_err}')
        return None
    except Exception as e:
        print(f'An error occurred accessing URL {url}: {e}')
        return None


driver = webdriver.Chrome()

try:
    url = 'https://bigfuture.collegeboard.org/college-search/filters'
    driver.get(url)
    time.sleep(5)

    scroll_to_bottom(driver)
    click_show_more(driver, 5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    anchors = soup.find_all('a', class_='cs-college-card-college-name-link')
    base_url = 'https://bigfuture.collegeboard.org'

    with open('colleges_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        headers = [
            'College Name', 'URL', 'Acceptance Rate', 'Regular Application Due', 'SAT Range', 'ACT Range',
            'High School GPA', 'High School Rank', 'SAT/ACT Scores', 'Recommendations', 'Application Fee',
            'Application Types Accepted', 'Graduation Rate', 'Majors Available', 'Student to Faculty Ratio',
            'Retention Rate', 'Majors and Degrees', 'Setting', 'Undergraduate Students',
            'Average per Year for Campus Housing', 'Sports', 'First Years in College Housing', 'Housing Options',
            'Activities', 'Student Body'
        ]
        writer.writerow(headers)

        for anchor in anchors:
            try:
                href = anchor['href']
                full_url = href if href.startswith(base_url) else base_url + href
                print(f'Scraping {full_url}')
                college_data = scrape_content(full_url)
                if college_data:
                    writer.writerow([
                        college_data.get('College Name', ''),
                        college_data.get('URL', ''),
                        college_data.get('Acceptance Rate', ''),
                        college_data.get('Regular Application Due', ''),
                        college_data.get('SAT Range', ''),
                        college_data.get('ACT Range', ''),
                        college_data.get('High School GPA', ''),
                        college_data.get('High School Rank', ''),
                        college_data.get('SAT/ACT Scores', ''),
                        college_data.get('Recommendations', ''),
                        college_data.get('Application Fee', ''),
                        college_data.get('Application Types Accepted', ''),
                        college_data.get('Graduation Rate', ''),
                        college_data.get('Majors Available', ''),
                        college_data.get('Student to Faculty Ratio', ''),
                        college_data.get('Retention Rate', ''),
                        college_data.get('Majors and Degrees', ''),
                        college_data.get('Setting', ''),
                        college_data.get('Undergraduate Students', ''),
                        college_data.get('Average per Year for Campus Housing', ''),
                        college_data.get('Sports', ''),
                        college_data.get('First Years in College Housing', ''),
                        college_data.get('Housing Options', ''),
                        college_data.get('Activities', ''),
                        college_data.get('Student Body', '')
                    ])
                print('-' * 70)
            except Exception as e:
                print(f'An error occurred while scraping {full_url}: {e}')
except Exception as e:
    print(f'An error occurred: {e}')
finally:
    driver.quit()
