import datetime
import discord

def timeparse(duration,maxdays,maxseconds):
    success = True
    c = ""
    hours = 0
    seconds = 0
    for letter in duration:
        if letter.isalpha():
            letter = letter.lower()
            try: c = int(c) 
            except: 
                success = False  
                break
            if letter == 'w': hours += c*168 
            elif letter == 'd': hours += c*24
            elif letter == 'h': hours += c
            elif letter == 'm': seconds += c*60
            elif letter == 's': seconds += c
            else: 
                success = False
                break
            c = ""
        else:
            c += letter
    if c != "" or not success:
        return 'I could not parse your timing input!\n\nValid Time Inputs:\n`w` - weeks\n`d` - days\n`h` - hours\n`m` - minutes\n`s` - seconds\n\nExamples: `2w`, `2h30m`, `10s`'
    added = datetime.timedelta(hours = hours,seconds = seconds)
    max = datetime.timedelta(days = maxdays,seconds= maxseconds)
    if added > max:
        return f"Your time duration goes over the maximum time!"
    return added