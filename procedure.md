# Running a HighEdWeb Association conference evaluations

Broadly, running evaluations consists of:

* Creating evaluations in Survey Monkey
* Linking to the evaluations on the conference's schedule page
* (for Annual) Manually enter data from paper responses
* Extracting the response data from Survey Monkey
* Creating excel reports from that data
* Close the collectors on SurveyMonkey

The first two steps are largely manual, for now, unfortunately.  Good times.

## Creating evaluations in Survey Monkey

For each session, do the following.  I set up a spreadsheet with columns for Track Code, Session Number and Title which computes the correct survey name in a fourth column.

1. click Create Survey
2. select Edit a copy of an Existing Survey.  Select `2014 Session Eval Template`.  It's important to keep using this template so we can compare data accurately across conferences and years.  
3. Enter the new Survey's title.  It varies by conference, but it's like `2014 HighEdWeb Annual Conference`. Click `Let's Go`
4. Click on the dark blue bar that has the Survey's title in it.  Check "Use Nickname".  Set the nickname to `{2 letter conference code} {Year} Session {TrackCode}{SessionNumber} The Actual Title Of The Session`.  Formatting here is important for the extraction process. Click `Save`
5. Edit where it says "Session Title: jQuery and Ajax" (it's the first section of the survey) to read `Session Title: The Actual Title Of The Session`
6. Click `Next`
7. Copy the Web Link to that spreadsheet you're keeping.  This is where you'll send respondents.  It'll be the link from the conference schedule.
8. Click `Manual Data Entry`.  Click `+ New Response`.  Copy the URL of the new tab/window.  This is the "manual data entry" link which will be used for inputting paper responses, if we're collecting them for the conference.  Annual does, regionals do if they'd like.
9. Rinse, repeat.  Fun, huh?  We should PhantomJS script this process.

## Linking to the evaluations 

Left as an exercise for the reader.  I've rigged up javascript on each conference's schedule page which reads a static JS object and emits visible buttons which say "Evaluate" once 30 minutes have passed from the session's start time.

## Manually enter data from paper responses

Remember those links we collected while creating the surveys?  Visit one and fill out the form.  For 2014 Annual I made a grid of all 70 or so, and the data entry folks would just click on the session code to get to the proper form.

## Extracting response data from Survey Monkey

### one-time setup

```
$ git clone https://github.com/SurveyMonkey/python_guides.git
$ virtualenv evals_venv
$ . evals_venv/bin/activate
$ pip install -r requirements.txt
$ pip install ipython
```

### Loading data from SurveyMonkey into the local cache

1. make sure the settings at the top of `smpy.py` match the conference you're working on
2. Run the following
```
$ export SM_API_KEY=xxx
$ export SM_API_SECRET=yyy
$ . evals_venv/bin/activate
$ python smpy.py

> update_likerts_for_current_conference()
> persist()
> exit
```

## Creating excel reports from that data

1. make sure the settings at the top of `smpy.py` match the conference you're working on
2. Run the following
```
$ . evals_venv/bin/activate
$ python smpy.py

> make_xlsx()
> make_xlsx_for_presenters()
> exit
```

## Close the collectors on Survey Monkey

Each evaluation on Survey Monkey has one "web collector."  That should be disabled after the conference is over.