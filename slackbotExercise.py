#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import time
import requests
import json
import csv

# Set your config variables from the config.json file
with open('config.json') as f:
    settings = json.load(f)
    USERTOKENSTRING = settings['USERTOKENSTRING']
    URLTOKENSTRING = settings["URLTOKENSTRING"]
    TEAMNAMESTRING = settings["TEAMNAMESTRING"]
    CHANNEL = settings["CHANNEL"]
    CHANNEL_ID = "C06D39D50"


# Extracts online users from Slack API
def extractSlackUsers(token):
    # Set token parameter of Slack API call
    tokenString = token
    params = {"token": tokenString, "channel": CHANNEL_ID}

    # Capture Response as JSON
    response = requests.get("https://slack.com/api/channels.info", params=params)
    responseUsers = requests.get("https://slack.com/api/users.list", params=params)
    usersGroup = json.loads(response.text, encoding='utf-8')["channel"]["members"]
    allUsers = json.loads(responseUsers.text, encoding='utf-8')["members"]

    def foundUser(user):
        for userId in usersGroup:
            if userId == user["id"]:
                return True
        return False

    users = filter(foundUser, allUsers)

    def findUserNames(x):
        if getStats(x) is False:
            return None
        name = "@" + x["name"].encode('utf-8')
        return name.encode('utf-8')

    def getStats(x):
        params = {"token": tokenString, "user": x["id"]}
        response = requests.get("https://slack.com/api/users.getPresence", params=params)
        status = json.loads(response.text, encoding='utf-8')["presence"]
        return status == "active"

    return filter(None, list(map(findUserNames, users)))


# Selects Next Time Interval and Returns the Exercise
def selectExerciseAndStartTime():

    # Exercise (2 Forms of Strings)
    exercises = [" отжиманий ", " отжиманий ", " пробежать этажей ", " приседаний ", " секунд сидения у стены "]
    exerciseAnnouncements = ["отжимания", "отжимания", "пробежаться по летнице", "приседания", "сидение у стены"]

    # Random Number generator for Reps/Seconds and Exercise
    nextTimeInterval = random.randrange(30*60, 50*60)
    exerciseIndex = random.randrange(0, 5)

    # Announcement String of next lottery time
    lotteryTimeString = "Следующая лотерея на " + str(exerciseAnnouncements[exerciseIndex]) + " будет через " + str(nextTimeInterval/60) + " минуту"

    # POST next lottery announcement to Slack
    requests.post("https://" + TEAMNAMESTRING + ".slack.com/services/hooks/slackbot?token="+URLTOKENSTRING+"&channel=%23"+CHANNEL, data=lotteryTimeString)

    # Sleep until next lottery announcement
    time.sleep(nextTimeInterval)

    # Return exercise
    return str(exercises[exerciseIndex])


# Selects the exercise lottery winner
def selectPerson(exercise):

    # Select number of reps
    exerciseReps = random.randrange(10, 20)

    # Pull all users from API
    slackUsers = extractSlackUsers(USERTOKENSTRING)

    # Select index of team member from array of team members
    selection = random.randrange(0, len(slackUsers))

    # Select lottery winner
    lotteryWinnerString = str(exerciseReps) + str(exercise) + ", прямо сейчас для " + slackUsers[selection]
    print lotteryWinnerString

    # POST to Slack
    requests.post("https://" + TEAMNAMESTRING + ".slack.com/services/hooks/slackbot?token="+URLTOKENSTRING+"&channel=%23"+CHANNEL, data=lotteryWinnerString)

    # Record exercise entry in csv
    with open("results.csv", 'a') as f:
        writer = csv.writer(f)
        writer.writerow([slackUsers[selection], exerciseReps, exercise])

for i in range(10000):
    exercise = selectExerciseAndStartTime()
    selectPerson(exercise)


