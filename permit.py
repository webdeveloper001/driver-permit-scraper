# -*- coding: utf-8 -*-
import csv     
import requests
import json
import errno
from datetime import datetime
from bs4 import BeautifulSoup 
import urllib
import sys
import os
import math
reload(sys)
sys.setdefaultencoding('utf8')
class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"

urllib._urlopener = AppURLopener()

h_list = open('points.csv')
csv_reader = csv.reader(h_list, delimiter=',')

csv.register_dialect('myDialect1',
	  quoting=csv.QUOTE_ALL,
	  skipinitialspace=True)

write_file = open('Alabama.csv', 'a')
csv_writer = csv.writer(write_file, dialect='myDialect1')

csv_writer.writerow(['State', 'Test Type', 'Description', 'Image', 'Case 1', 'Case 2', 'Case 3'])

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
})


# for item in csv_reader:
#     new_item = item
#     if item[3] != '':
states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'Sault Ste. Marie', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'Washington DC', 'West Virginia', 'Wisconsin', 'Wyoming']

# missed = ['Colorado', 'Connecticut', 'Illinois', 'Iowa', 'Arkansas', 'California']
# missed = ['Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts']
# missed = ['Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada']

# missed = ['New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota']
# missed = ['Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island']
# missed = ['South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont']
# missed = ['Virginia', 'Washington', 'Washington DC', 'West Virginia', 'Wisconsin', 'Wyoming']
# missed = ['Nevada']


for state in states:
    # state = states[sindex]
    # state = missed[sindex]
    try:
        os.mkdir('states/' + state)
        os.mkdir('states/' + state + '/images')
    except OSError as e:
        
        continue
    url = 'https://dmv-permit-test.com/{}/practice-test-{}.html?page={}'
    for testtype in range(1, 100):
        try:
            r = session.get(url.format(state.replace(' ', '-'), testtype, 1))
        except (requests.exceptions.ConnectionError):
            # ignore pages with errors
            continue
        soup = BeautifulSoup(r.text, features="html.parser")
        if soup.find('h1') == None:
            break
        testtitle = soup.find('h1').text
        numbers = int(soup.find('i', class_="fa-question-circle").parent.parent.findAll('td')[1].text)
        correct = int(soup.find('i', class_="fa-check").parent.parent.findAll('td')[1].text)
        min_age = (soup.find('i', class_="fa-calendar-alt").parent.parent.findAll('td')[1].text.strip())
        passing_score = str(int(float(correct) / numbers * 100)) + '%'
        state_code = soup.findAll('div', class_='box-title')[1].text.strip().split(' ')[0]
        write_file = open('states/'+ state + '/' + testtitle + '-' + str(testtype) + '.csv', 'a')
        csv_writer = csv.writer(write_file, dialect='myDialect1')
        csv_writer.writerow(['Test', testtitle, 'State', state, 'State Code', state_code, 'Test Size', numbers, 'Passing Grae', str(correct) + '(' + passing_score + ')'])
        csv_writer.writerow([])
        csv_writer.writerow(['Question ID', 'Question Text', 'Image for Question', 'Answer1 Text', 'Answer1 Correct?', 'Answer2 Text', 'Answer2 Correct?', 'Answer3 Text', 'Answer3 Correct?', 'Answer4 Text', 'Answer4 Correct?'])
        print(int(math.ceil(float(numbers) / 10) + 1))
        for page in range(1, int(math.ceil(float(numbers) / 10) + 1)):
            try:
                r = session.get(url.format(state.replace(' ', '-'), testtype, page))
            except (requests.exceptions.ConnectionError):
                # ignore pages with errors
                continue
            # print(r.text.split('ans = '))
            correct_answers = json.loads(r.text.split(';var ans = ')[1].split('; var ')[0])
            soup = BeautifulSoup(r.text, features="html.parser")

            print(soup.find('h1').text)
            questions = soup.findAll('div', class_='question')
            for index in range(0, len(questions)):
                item = []
                question = questions[index]
                questions_id = question.attrs['id']
                item.append(questions_id)
                description = question.findAll('div')[0].findAll('span')[0].text + question.findAll('div')[0].findAll('span')[1].text
                item.append(description)
                image = ''
                if question.find('div', class_='image').find('img'):
                    image = question.find('div', class_='image').find('img').attrs['src']
                    urllib.urlretrieve(image, 'states/'+ state + '/images/' + image.split('/')[len(image.split('/')) - 1])
                    image = 'images/' + image.split('/')[len(image.split('/')) - 1]
                item.append(image)
                answers = question.findAll('span', class_='answer')
                for aindex in range(0, len(answers)):
                    item.append(answers[aindex].text)
                    if correct_answers[index] == aindex + 1:
                        item.append(True)
                    else:
                        item.append(False)
                csv_writer.writerow(item)
                print(item)