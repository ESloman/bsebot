# file for daily vwordle reminders
# when sending a wordle reminder message, it will pick one of these at random
# message will be chosen randomly, but based on some dynamically created odds
# use a tuple to hardcode some odds
# the '{mention}' bit is where the user mention will be inserted
# to add a new one, simply add a new line

MESSAGES = [
    "Hey {mention}, don't forget to do your Wordle today!",
    "Hey {mention}, you absolute knob, you haven't done your Wordle yet!",
    "Guess what? {mention} is a fucking prick. Also, they didn't do their Wordle.",
    "Do your Wordle or die, {mention}.",
    "Don't forget to do your wordle today {mention}.",
    "{mention} hasn't done their Wordle today. Are they stupid?",
    "Daddy wants you to complete your Wordle today {mention}",
    "{mention}\nRoses are red\nViolets are blue\nI've done my Wordle\nDon't forget to do yours too!",

    # HARD-CODED ODDS EXAMPLE
    # tuple with message string as first item, chance (roughly out of 100) as a float
    # ("This is a super rare message {mention}", 1.0)
]
