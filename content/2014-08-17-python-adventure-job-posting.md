Title: Python Adventure: Our command line based job posting.
Date: 2014-08-18 13:00
Category: meta
Tags: meta
Slug: python-adventure-job-posting
Author: Chanux
Summary: We created an awesome job posting that worked in the terminal.

Back in October 2013 we were looking for a Software Engineer that would speak Python and willing to go in adventures. I thought this required a special person. A common job posting sounded like too bland of an option for this. Hence the adventure was born.

![original python adventure job posting](/images/python-adventure.jpg)

The idea is not original. I have seen something similar done before and really loved it. Anyhow there were not much info to be found online about it (even back when I did this). So I thought of giving life back to the idea. (My memory fails me so hard I can remember zero to nothing about original work :( ).

So the idea was, the potential candidates use curl (or wget) to retrieve the job posting. We devised an ASCII art version of thinkcube logo and the text was colored green to mimic the old terminals (Still a popular choice of color for terminal text IMHO). I added a nice streaming effect later so the initial praise we received were for a version less cooler than what you see now.

Yes it's still online! Check it yourself.

`curl http://thinkcube.com/adventure`

I got one thing wrong in the text there. It sounds like we only accept txt files but we do accept txt, pdf, odt, doc and docx :-/. The text looks the same probably because I'm too lazy.

For anyone interested, we have posted the [code](https://github.com/thinkcube/python-adventure) on our github account.

We used gunicorn behind an nginx proxy to serve the app. There is a smaple nginx config in repository. To manage processes, we have used Circus since we were playing with it at the time. It's a nice tool you should check out so make this a chance.

So if you are interested in what we do and like to be a part of the team, please apply :)
