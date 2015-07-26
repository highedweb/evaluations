# coding=utf-8
# This program is checked in as-is, without any consideration for making it more modular or better organized.

# TODO: make it more modular and better organized
# TODO: handle page sizes of data > 1000 (which is the SM default)
# TODO: handle blank answers on the likert stuff (and what about avg/stddev in excel?  does blank work for that?)

# format: AN, NY, SC, MI, AL  then year.  Same as at the beginning of survey titles in Survey Monkey.
conference_prefix = 'AL 2015'
# store the data downloaded from surveymonkey here
persistence_filename = 'data/2015/al-2015-data.pkl'
# output the resulting spreadsheet here
excel_filename = 'data/2015/al-2015-results.xlsx'
# and the version for presenters can go here
presenter_excel_filename = 'data/2015/al-2015-results-for-presenters.xlsx'

from IPython import embed
from python_guides.guides.api_service import api_service
import pickle
import os.path
import pprint
from time import sleep
from datetime import datetime, timedelta
import os

api = api_service.ApiService(os.environ['SM_API_KEY'], os.environ['SM_API_PASSWD'])

if os.path.isfile(persistence_filename):
  with open(persistence_filename, 'rb') as f:
    persisted_data = pickle.load(f)
else:
  persisted_data = {}

def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]

def one_second_later(t):
  return (datetime.strptime(t, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
def date_for(t):
  return datetime.strptime(t, '%Y-%m-%d %H:%M:%S')

def get_session_survey_identifiers_for(cp):
  if 'survey_list' in persisted_data and 'survey_list_start_date' in persisted_data:
    options = { 'start_date': one_second_later(persisted_data['survey_list_start_date']),
              }
  else:
    persisted_data['survey_list'] = {}
    persisted_data['survey_list_start_date'] = '2014-01-01 00:00:00'
    options = {}
  options['title'] = cp + ' Session'
  options['fields'] = ['title', 'date_created']
  r = {'status': 1}
  pause = 2
  while r['status'] == 1:
    sleep(pause)
    pause = pause + 2
    pprint.pprint("Getting survey list with options:")
    pprint.pprint(options)
    r = api.get_survey_list(options)
  pprint.pprint(r)
  last_date = persisted_data['survey_list_start_date']
  for s in r['data']:
    last_date = s['date_created']
    persisted_data['survey_list'][s['survey_id']] = s
  persisted_data['survey_list_start_date'] = last_date

def get_session_survey_details_for(survey_id):
  r = {'status': 1}
  pause = 2
  while r['status'] == 1:
    sleep(pause)
    pause = pause + 2
    pprint.pprint("Getting survey details with options:")
    pprint.pprint({ 'survey_id': survey_id })
    r = api.get_survey_details({ 'survey_id': survey_id })
  pprint.pprint(r)
  if 'survey_id' in r['data']:
    if 'survey_details' not in persisted_data:
      persisted_data['survey_details'] = {}
    persisted_data['survey_details'][survey_id] = r['data']

def get_latest_surveys_for(cp):
  get_session_survey_identifiers_for(cp)
  for survey_id in persisted_data['survey_list']:
    if 'survey_details' not in persisted_data:
      persisted_data['survey_details'] = {}
    if survey_id not in persisted_data['survey_details']:
      get_session_survey_details_for(survey_id)
      
def update_likerts_for_current_conference():
  get_latest_surveys_for(conference_prefix)
  for survey_id in persisted_data['survey_details']:
    get_response_data_for(survey_id)

def get_questions_for(survey_id):
  if survey_id in persisted_data['survey_details']:
    return sorted([{ "heading": q['heading'], "question_id": q['question_id'], "position": q['position'] } for q in persisted_data['survey_details'][survey_id]['pages'][0]['questions'] if q['type']['family'] != 'presentation'], key=lambda k: k['position'])
  else:
    return []

def get_likert_questions_for(survey_id):
  if survey_id in persisted_data['survey_details']:
    return sorted([{ "heading": q['heading'], "question_id": q['question_id'], "position": q['position'] } for q in persisted_data['survey_details'][survey_id]['pages'][0]['questions'] if q['type']['family'] != 'presentation' and q['answers']], key=lambda k: k['position'])
  else:
    return []

def reset_response_data_for(survey_id):
  if survey_id not in persisted_data['survey_details']:
    persisted_data['survey_details'][survey_id] = {}
  persisted_data['survey_details'][survey_id]['respondents'] = {}
  persisted_data['survey_details'][survey_id]['respondent_list_start_date'] = '2014-01-01 00:00:00'

def get_response_data_for(survey_id):
  if survey_id not in persisted_data['survey_details']:
    persisted_data['survey_details'][survey_id] = {}
  if 'respondents' not in persisted_data['survey_details'][survey_id]:
    persisted_data['survey_details'][survey_id]['respondents'] = {}    
    persisted_data['survey_details'][survey_id]['respondent_list_start_date'] = '2014-01-01 00:00:00'
  options = { 'survey_id': survey_id, 'start_date': one_second_later(persisted_data['survey_details'][survey_id]['respondent_list_start_date']), 'fields': ['date_start','collection_mode']}
  pprint.pprint("Retrieving respondents from %s or later" % (options['start_date']))
  r = {'status': 1}
  pause = 2
  while r['status'] == 1:
    sleep(pause)
    pause = pause + 2
    pprint.pprint("Getting respondent list with options:")
    pprint.pprint(options)
    r = api.get_respondent_list(options)
  last_date = persisted_data['survey_details'][survey_id]['respondent_list_start_date']
  pprint.pprint(r)
  for respondent in r['data']:
    persisted_data['survey_details'][survey_id]['respondents'][respondent['respondent_id']] = respondent
    last_date = respondent['date_start']
  persisted_data['survey_details'][survey_id]['respondent_list_start_date'] = last_date
  respondent_ids_to_retrieve_data = [respondent['respondent_id'] for respondent in persisted_data['survey_details'][survey_id]['respondents'].values() if 'response' not in respondent]
  for chunk in chunks(respondent_ids_to_retrieve_data, 100):
    pprint.pprint('Retrieving:')
    pprint.pprint(chunk)
    r = {'status': 1}
    pause = 2
    while r['status'] == 1:
      sleep(pause)
      pause = pause + 2
      pprint.pprint("Getting responses with options:")
      pprint.pprint({ 'survey_id': survey_id, 'respondent_ids': chunk })
      r = api.get_responses({ 'survey_id': survey_id, 'respondent_ids': chunk })
    pprint.pprint(r)
    for response in r['data']:
      persisted_data['survey_details'][survey_id]['respondents'][response['respondent_id']]['response'] = response['questions']

def likert2number(likert):
  return { "Strongly Agree": 5, "Agree": 4, "Neutral": 3, "Disagree": 2, "Strongly Disagree": 1}[likert]

@memoize
def answerdict(survey_id):
  return {key: value for (key, value) in [item for sublist in [ [(a['answer_id'], a['text']) for a in ag]  for ag in [q['answers'] for q in persisted_data['survey_details'][survey_id]['pages'][0]['questions'] if q['answers'] and q['type']['family'] != 'presentation']] for item in sublist] }

def answer2text(survey_id, answer_id):
  return answerdict(survey_id)[answer_id]

def massaged_likert_responses(survey_id, response):
  """ order by page order in survey questions, pull out responses from the response array """
  return [likert2number(answer2text(survey_id, [ x for x in response['response'] if x['question_id'] == question['question_id']][0]['answers'][0]['row'])) if (question['question_id'] in [resp['question_id'] for resp in response['response']]) else '-' for question in get_likert_questions_for(survey_id)]
    
def answer_to_question_by_position(survey_id, respondent_id, position):
  question_id = [q['question_id'] for q in persisted_data['survey_details'][survey_id]['pages'][0]['questions'] if q['position'] == position][0]
  return [answer for answer in persisted_data['survey_details'][survey_id]['respondents'][respondent_id]['response'] if answer['question_id'] == question_id]

def responses_for(survey_id):
  return persisted_data['survey_details'][survey_id]['respondents'].values();

def massaged_likert_responses_for(survey_id):
  return [ (response['respondent_id'], response['date_start'], massaged_likert_responses(survey_id, response), response['collection_mode']) for response in sorted(responses_for(survey_id), key=lambda k:date_for(k['date_start'])) ]

def persist():
  with open(persistence_filename, 'wb') as f:
    pickle.dump(persisted_data, f)


import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

def make_xlsx():
  workbook = xlsxwriter.Workbook(excel_filename)
  summary_worksheet = workbook.add_worksheet('Summary')
  summary_worksheet.write(0, 1, "Average")
  summary_worksheet.write(0, 2, "Std Dev")
  summary_worksheet.write(0, 3, "N")

  summary_row = 1
  for survey_id in sorted(persisted_data['survey_details'], key=lambda k: persisted_data['survey_details'][k]['nickname']):
    n = 0
    sheet_name = persisted_data['survey_details'][survey_id]['nickname'][0:31]
    sheet_name = sheet_name.replace("-", "_")
    sheet_name = sheet_name.replace("'", "_")
    sheet_name = sheet_name.replace(",", "_")
    sheet_name = sheet_name.replace(" ", "_")
    #sheet_name = sheet_name.replace("…", "_")
    sheet_name = sheet_name.replace("!", "_")
    sheet_name = sheet_name.replace("[", "_")
    sheet_name = sheet_name.replace("]", "_")
    sheet_name = sheet_name.replace("{", "_")
    sheet_name = sheet_name.replace("}", "_")
    sheet_name = sheet_name.replace(":", "_")
    sheet_name = sheet_name.replace("*", "_")
    sheet_name = sheet_name.replace("?", "_")
    sheet_name = sheet_name.replace("/", "_")
    sheet_name = sheet_name.replace("\\", "_")
    sheet_name = sheet_name.replace("+", "_")
    sheet_name = sheet_name.replace("=", "_")
    sheet_name = sheet_name.replace("!", "_")
    sheet_name = sheet_name.replace("(", "_")
    sheet_name = sheet_name.replace(")", "_")
    worksheet = workbook.add_worksheet(sheet_name)
    row = 0
    col = 1
    worksheet.write(row, col, 'collection_mode')
    col = col + 1
    for q in get_likert_questions_for(survey_id):
      worksheet.write(row, col, q['heading'])
      col = col + 1
    worksheet.write(row, col, "Average")
    row = row + 1
    avg_col = 0
    pprint.pprint("Getting massaged_likert_responses_for(survey_id)")
    pprint.pprint(survey_id)
    pprint.pprint(massaged_likert_responses_for(survey_id))
    for (respondent_id, dt, responses, collection_mode) in massaged_likert_responses_for(survey_id):
      n = n + 1
      avg_col = len(responses) + 2
      col = 0
      worksheet.write(row, col, dt)
      col = col + 1
      worksheet.write(row, col, collection_mode)
      for r in responses:
        col = col + 1
        worksheet.write(row, col, r)
      if col > 0:
        worksheet.write(row, col + 1, '=iferror(AVERAGE(%s:%s), "-")' % (xl_rowcol_to_cell(row, 1), xl_rowcol_to_cell(row, avg_col - 1)))
      l = answer_to_question_by_position(survey_id, respondent_id, 8)
      if len(l) >= 1:
        worksheet.write(row, col + 2, l[0]['answers'][0]['text'])
      row = row + 1
    if row > 1:
      worksheet.write(row, avg_col, '=iferror(AVERAGE(%s:%s), "-")' % (xl_rowcol_to_cell(1, avg_col), xl_rowcol_to_cell(row - 1, avg_col)))
    worksheet.write(row, avg_col + 1, '=iferror(STDEV(%s:%s), "-")' % (xl_rowcol_to_cell(1, avg_col), xl_rowcol_to_cell(row - 1, avg_col)))
    worksheet.write(0, 0, "N = %d" % n)
    summary_worksheet.write(summary_row, 0, persisted_data['survey_details'][survey_id]['nickname'])
    summary_worksheet.write(summary_row, 1, '=%s!%s' % (sheet_name, xl_rowcol_to_cell(row, avg_col)))
    summary_worksheet.write(summary_row, 2, '=%s!%s' % (sheet_name, xl_rowcol_to_cell(row, avg_col+1)))
    summary_worksheet.write(summary_row, 3, n)
  
    summary_row = summary_row + 1

  workbook.close()

def make_xlsx_for_presenters():
  workbook = xlsxwriter.Workbook(presenter_excel_filename)

  summary_row = 1
  for survey_id in sorted(persisted_data['survey_details'], key=lambda k: persisted_data['survey_details'][k]['nickname']):
    n = 0
    sheet_name = persisted_data['survey_details'][survey_id]['nickname'][0:31]
    sheet_name = sheet_name.replace("-", "_")
    sheet_name = sheet_name.replace("'", "_")
    sheet_name = sheet_name.replace(",", "_")
    sheet_name = sheet_name.replace(" ", "_")
    #sheet_name = sheet_name.replace("…", "_")
    sheet_name = sheet_name.replace("!", "_")
    sheet_name = sheet_name.replace("[", "_")
    sheet_name = sheet_name.replace("]", "_")
    sheet_name = sheet_name.replace("{", "_")
    sheet_name = sheet_name.replace("}", "_")
    sheet_name = sheet_name.replace(":", "_")
    sheet_name = sheet_name.replace("*", "_")
    sheet_name = sheet_name.replace("?", "_")
    sheet_name = sheet_name.replace("/", "_")
    sheet_name = sheet_name.replace("\\", "_")
    sheet_name = sheet_name.replace("+", "_")
    sheet_name = sheet_name.replace("=", "_")
    sheet_name = sheet_name.replace("!", "_")
    sheet_name = sheet_name.replace("(", "_")
    sheet_name = sheet_name.replace(")", "_")
    worksheet = workbook.add_worksheet(sheet_name)
    row = 0
    col = 0
    for q in get_likert_questions_for(survey_id):
      worksheet.write(row, col, q['heading'])
      col = col + 1
    row = row + 1
    pprint.pprint("Getting massaged_likert_responses_for(survey_id)")
    pprint.pprint(survey_id)
    pprint.pprint(massaged_likert_responses_for(survey_id))
    for (respondent_id, dt, responses, collection_mode) in massaged_likert_responses_for(survey_id):
      n = n + 1
      col = 0
      for r in responses:
        worksheet.write(row, col, r)
        col = col + 1
      l = answer_to_question_by_position(survey_id, respondent_id, 8)
      if len(l) >= 1:
        worksheet.write(row, col, l[0]['answers'][0]['text'])
      row = row + 1

  workbook.close()


embed()
persist()

