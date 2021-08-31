---
layout: post
title: Passing the HAM Radio Exam and Thoughts on Making It Better
date:  2021-08-06 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

A couple of hours ago, I passed the HAM radio exams for the Technician and the General license. 
I didn't practice for the highest level, Amateur Extra, so I skipped that one for now.

![Screenshot of question T1A05](/assets/ham_exam/T1A05.png)

According to question T1A05 of the technical exam question pool, it will be a few days before 
I'm officially allowed to be the control operator, the one who presses the transmit button, 
of a HAM radio transceiver. For that, my name needs to show up in some FCC database. 
But I'm in no hurry, because despite passing the exams, my actual knowledge is woefully
lacking.

The decision process to get these license was a bit long winded, and went as follows:

* 3 years ago, I bought 2 dirt cheap 
  [Baofeng UV-5R handheld transceivers](https://www.amazon.com/Baofeng-UV-5R-136-174-400-480Mhz-1800mAh/dp/B074XPB313).

    ![Picture of Baofeng UV-5R](/assets/ham_exam/Baofeng_UV-5R.jpg)

    Many HAM enthousiasts hate these things, because their quality isn't great, and 
    some of them violate the FCC requirements about spurious emissions etc. But: 
    dirt cheap.

* I never used these handhelds because you need an FCC HAM radio license to transmit with them.
* But recently, I acquired a cool HP 8590B spectrum analyzer through Craiglist.

    ![Picture of HP 8590B Spectrum Analyzer](/assets/ham_exam/hp8590b.jpg)

* I want to experiment with RF: do some measurements on the handhelds, maybe build 
  some RF antennas and filters, who knows...
* All of which would require an FCC license...

# How to Get a HAM Radio License 

So a week ago, I started looking into the requirements, and it’s really quite simple:

* There are 3 levels. In order of increasing sophistication: Technician, General, and Amateur Extra.
* There’s an exam for each level.
* For each level, there's a pool of 425, 450, and 650 questions resp. The pool of questions stays
  fixed for a couple of years.
* The exam itself consists of 35, 35, and 50 multiple choice question.
* You need to a score of at least 74% question to pass an exam.

Since the pool of questions stays constant for a couple of years, there is plenty of study 
material in the form of books, YouTube videos and websites with trial exams, flash cards etc.

If you decide to buy a book that focuses on the actual question pool, make sure it targets the
current version. Today's exams have the following expiration date:

| Level         | Expiration Date | Question Pool Size | Questions per Test |
|---------------|-----------------|------------------------------------------
| Technician    | Jun 30, 2022    | 428 | 35 |
| General       | Jun 30, 2023    | 454 | 35 |
| Amateur Extra | Jun 30, 2024    | 621 | 50 |

For each level, the pool of questions is divided into 9 categories (safety, 
commission rules, operating procedures, practical circuits, ...) And within
each category, there are subcategories too.

The actual exam contains a fixed ratio of questions from each category.

# How I Prepared for the Tests

The best way to learn really learn something is to study a subject with the goal of learning
something, and then use a exam as a way to confirm and prove your understanding. It's also
the only practical way if there is no fixed set of questions. 

The other way is studying to the test, a close cousin of teaching to the test: your goal is
to pass, preferably with a little effort as possible. 

Since the HAM exams have a fixed pool of questions, studying to the test is totally possible,
and without any books in hand, and exams scheduled 5 days later, I really didn't have much 
choice. (Not that I would have made a different choice if I had more time, I just wanted to
get this over with.)

My plan was to make sure to get all the questions by reasoning, intuition, 
basic math and physics, and, failing all that, rote memorization.

My tool of choice was [HamExam.org](www.hamexam.org). It has everything need: the pool of questions
per exam, flash cards, practice exams, and detailed statistics tracking.

*Learning something new is very personal. I've always been good at remembering things for a short
time and forget about them as soon as I don't need it anymore, and I probably relied on that
way too much during my studying days. Another thing to keep in mind is that I have an
electronics degree. And even though it has been more than 25 years since I had some college level 
classes about electromagnetic waves, many aspects of the HAM exam heavily favor such a background,
which is one of the issues as have with the exam.*

My learning process for the technical exam was as follows:

1. Create an account on [HamExam.org](www.hamexam.org).
1. Read through the [question pool of the category](https://hamexam.org/view_pool/15-Technician) I want 
   to learn next.

    * I highlight the right question, it's option at the top of the page, but also show the incorrect answers. 
    There are often incorrect answers that help me remember the correct one. This is especially true
    when I want to learn numbers by heart.

    * When there are terms in a question that I don't understand, I looked them up on Wikipedia. 

1. In the [Filters page](https://hamexam.org/filters/15-Technician), I disable all the questions except 
   for the category I want to study.
1. Answer questions in the [Flash Cards](https://hamexam.org/flash_cards/15-Technician) as long
   as needed. My goal is to be able to answer all the questions right with reasonable consistency.

Repeat for all 9 subcategories.

Once I felt comfortable about knowing most answers, I tried about 10 
[practise exams](https://hamexam.org/exam/15-Technician) to check that I'd score 85% or higher consistently.

As I wrote earlier, there are 4 different categories:

**Intuition or common sense**

There are a bunch of questions just requires some intuition or common sense.

The simplest ones are those related to safety. The FCC is an American organization, you can bet
that they're always going to go with the safest option.

![Screenshot of question T0B03: with is it safe to climb a tower without helper or observer](/assets/ham_exam/T0B03.png)

There are also those where there are multiple options that are somewhat reasonable, with an
"all of these choices are correct" option. For those, it's crucial to first check if one of the
options can't possible be correct, because that immediately invalidates the "everything is correct"
option, and reduces the number of potential right answers to just 2.

In the example below, Removing grounding is never a good idea, so that

![Screenshot of question T0B02: What is a good precaution to observe before climbing an antenna tower](/assets/ham_exam/T0B02.png)

Intuition and common sense will also develop itself after learning the right answer for different
questions. There are number of questions about special privileges and requirements to communicate with
different entities (space station, foreign amateurs, ...). What becomes apparent quickly is that all 
amateurs have pretty much the same rights and premissions with the only exception the frequency bands 
on which you're allowed to transmit.

![Screenshot of question T1B02: Which amateur radio stations may make contact with an amateur radio station on the International Space Station (ISS) using 2 meter and 70 cm band frequencies](/assets/ham_exam/T1B02.png)

Once you pick up a pattern like that, you'll be able to answer other questions correctly just the same.

![Screenshot of question T1C02: Who may select a desired call sign under the vanity call sign rules](/assets/ham_exam/T1C02.png)


Here are some other good examples of such a general pattern:

* inside the US, the FCC is almighty in setting the rules wrt radio communication, but they don't like to
  get involved in local squabbles. So overall rules are set by them, but they don't get involved in details
  like you interfering with the TV broadcast of your neighbor. 
* amateur radio is for amateur stuff. 

**Basic Math and Physics**

The most important formula to know is the following: 

*frequency (in MHz) x wavelength (in meters) = 300*

(The 300 comes from the fact that the speed of light is ~300 000 000 meters per second, which is another
question.)

Not only is there a question that asks for this formula, but questions use wavelength and 
frequency interchangeably, and you also need it for the general exam when there are questions
related to the length of antennas.

![Screenshot of question T1B04: Which amateur band are you using when your station is transmitting on 146.52 MHz](/assets/ham_exam/T1B04.png)

Category 5, whopping 57 questions, is all about basic physics: questions alone about coverting from MHz to GHz,
basic electronic principles, the defintion of voltage, current, and resistant and Ohm's Law.

![Screenshot of question T5B04: How many volts are equal to one microvolt](/assets/ham_exam/T5B04.png)

**Rote Memorization**

And then there's all the rest. Stuff that you just don't know and need to learn by heart.

It's a broad set of topics: FCC rules, amateur radio practices, RF propagation in the atmosphere, 
amateur equipment, electronic components etc.

A lot of these topics are trivial for an electrical engineer, but without such a background, I can imagine
them to be a major hurdle for many. And that's one of my biggest issues with the exam. See later.

# Taking the Exam in COVID Times 

Due to COVID, it's now possible to take the exams online, with a Zoom call.

In my case, the exams were administered by [GLAARG](https://glaarg.org), the Greater Los Angeles
Amateur Radio Group. The cost was $10, but that's per exam sessions: if you take more than
one exam, it's still only $10. (It's free for minors, active military and a bunch of others.)

The volunteer examinators were cordial and pleasant to talk to, but they take testing integrity 
very serious, as required by the rules. 

First they wanted to make sure that I had scored 85% or more on my practise exams and thus be confident 
about passing. There were a number of other test takers in my sessions, and since exams are 
administered one after the one, they don't want somebody giving a test a Hail Mary best shot while wasting
the time of everybody else.

The procedure is, IMO, seriously overdone:

* During the exam, not one, but 3 examinators observe your every move on camera to make sure you're 
  not glancing at electronic contraband or some Post-It Note on the wall.
* Your desk must be squeaky clean.
* You can't wear a smart watch.
* A family member entering the room results in an immediate disqualification.
* They even asked me to film the ceiling of my room to make sure no papers were attached there
  either.

I could understand this kind of paranoia if one were taking a certification test for nuclear submarine 
reactor technician, but it really makes no sense for an exam that can be passed successfully while
missing huge amount of IMO required knowledge. 

The duration of the exam really depends on your confidence and preparation. In my case, filling
in the 35 questions took far less time than the procedures before and after.

Since I was one of the first ones to log in, I was also one of the first ones to take the exam. The whole
thing took less than 30 min, and that's for 2 exams instead of one. I passed both.

# Thoughts on the Technician's Exam - Drop the Electronics Stuff

My overall feeling about the exam, especially the entry level technician one, is that it introduces
an unnecessary barrier by focusing too much on questions related to electronics. Yet at the same 
time, you can pass the test with a perfect score and still be clueless about some importnat aspects 
of HAM radio.

A beginner will almost certainly start by using a transceiver to communicate with others.
For that, it's important to know the rules, to know what's possible and what is not, how to operate 
equipment etc.  You're just not going to be building your own receivers and transmitters, 
but if you did, you'd only be able to be do that with a deep knowledge of electronics.

The current set of exams spreads the required knowledge about electronic circuits over
all 3 exams. It would make more sense to drop the truly technical stuff from the Technician's
level, and maybe even the General one. Understanding Ohm's Law or identifying a transistor in a 
schematic and nothing more will get you absolutely nowhere, so what's the point of asking?

By doing so, you're scaring away those who are only interested in communicating with others but who 
have no intention of ever building or repairing their own equipment.

And while questions are being wasted on these kind of topics, there are things missing too:

There's nothing about FRS (Family Radio Service), the walkie-talkies that can be bought in your local sports 
store, or GMRS (General Mobile Radio Service), a more advanced kind of personal radio service that requires 
one $70 license per family, valid for 10 years, but doesn't requires a test. I literally only learned
about these after the exams.

There could be more questions about equipment, equipment certifications, the different types and wattages etc.
A question about how you could get a $10000 fine by using a hacked walkie-talkie or a non-certified transceiver 
(my Boafengs!) on the bands allocated to FRS and GMRS would be instructive and memorable.

The Technician's exam has talks about antennas mostly in abstract terms.  It'd be so more useful
to have questions where you'd have to match pictures of antennas to their type. Meanwhile, the
the General exam has a lot of questions about Yagi antennas, but I got all of them correct without
knowing what a [Yagi antenna](https://en.wikipedia.org/wiki/Yagi–Uda_antenna) actually looks like. 
(Rote memorization...)

![Yagi antenna](/assets/ham_exam/Yagi_TV_antenna_1954.png)

It's obvious that studying to the test is the culprit in this case, but that brings me to the next point: 
a good set of questions can be designed so that you have to learn the material even if you study to the test. 

For example, technician's question T9A10 asks about the radiation strength pattern of half-wave dipole antenna: 

![Screenshot of question T9A10: In which direction does a half-wave dipole antenna radiate the strongest signal](/assets/ham_exam/T9A10.png)

The correct answer, "Broadside to the antenna", can be derived by eliminating of the other answers. 
But I still don't know what the means in practise. Had a question been asked with the pictures of 4 different 
radition patterns alongside, I'd actually have learned something.

BTW: did you know that the General license exam contains 6 questions about the requirements to administer,
not take, an exam? Is that really not something they could put on some website, easily found by Google for
the few for whom that'd be relevant? What a waste...

Thoughts:

* Inform about fines
* Inform about frequencies that require a different license or no license at all
    * FRS, GRS, MURS
* Move the useless technical parts (Ohm's law, electrical components, etc) to higher level license requirement
  and focus the Technician's license to using the thing correctly
* Use more pictures
    * ask test takers to identify different types of antennas (Yagi, Halo etc.), with the option to 


# Study rules

* When there's one nonsense option, this rules out that "all of these choices are correct"
* The FCC regulations are the law of the land for all things radio that happen in the US, or on
  a vessel that's registered in the US. But it doesn't rule local eletrical code wrt grounding etc.
* The 3 amateur licenses is only different in the kind of frequency bands you're allowed to 
  transmit in, and in the kind of exams that you're allowed to administer. There is no difference
  in terms of vanity call signs, restrictions in communicating with space ships (as long as you
  are using allowed frequency bands) etc.
* The FCC off-loads a lot of stuff to local volunteers: band plan, repeater channels, etc. There are
   no questions where you initiate contact with the FCC. (But the FCC could ask you to provide info etc.)
* FCC database is the source of truth wrt technician permissions.
* Grounding is important, and connecting the ground of different pieces of equipment is also important.
  Whenever one of the potential answer is "grounds are connected together", that's at least one of the
  correct answers.
* Fuses interrupt power for safety (fire etc). 
* Low voltage (<12V) can't shock, but high currents can burn
* RF works through electro-magnetic fields that is non-ionizing. Strong
  fields only result in RF burn/heating. It can't change generics.
* The power that matters for safety and limits is the power at the antenna.
* RF exposure is depending not only on power, but also location wrt antenna, radiation pattern.
* 50W is a key number of RF power exposure.
* Never interfere with others.
* Amateurs are always second class to others, except in emergencies. In those cases, licensed amateurs rule
  the airwaves.
* Frequency (in MHz) * wavelength (in m) = 300
* Voice: SSB is used for long distance, and limited bandwidth voice communications. Upper side band is used for
  everything except some HF bands.
* Old school fast scan TV (NTSC): 6MHz bandwidth, voice: ~2.4kHz bandwidth, morse: 150Hz BW. Based on that,
  you can derive the answer to a lot of questions related to bandwidthm, repeater offsets and filtering.
* Only talk about personal stuff, especially when transmitting with out-of-country people.
* Other countries can impose that you don't to interact with its subjects.
* Only plain, unencoded or unencrypted communication, except for space stations or radio controlled crafts.
* English is the answer, no other languages. Or morse code (CW). No dirty words ever.
* Music is only ever allowed when transmitting it to astronauts.
* You always have to identify yourself, every 10min and at the end of a transmission, except when talking to 
  a space station or radio controlled craft.
* A control operator is the one who handles the station (transceiver). Their license is what matter, not the one
  who owns the station. 
* Automatic control is when the transceiver automatically transmits, but even then, there needs to be a
  control operator overseeing the operation.
* When there's conflict, try to resolve it amicably. Running the FCC or some other body is never the right
  answer.
* When you're asked to diagnose an issue, very often (but not always!) the expected answer is "all of
  these choises are correct." 

| Name               |             HF             | VHF                       | UHF                       |
|--------------------|:--------------------------:|---------------------------|---------------------------|
| Frequency          |        3MHz - 30MHz        | >30MHz-300MHz             | >300MHz-3000MHz           |
| Wavelength         | 100m - 10m                 | <10m - 1m                 | <1m - 10cm                |
| Max Transmit Power |            200W            | 1500W                     |                           |
| Distance           | Long Distance (Ionosphere) | Line of sight, reflection | Line of sight, reflection |
| Licensing          | General, except for 10m    | Technician                | Technician                |
|                    |                            |                           |                           |
|                    |                            |                           |                           |
|                    |                            |                           |                           |
|                    |                            |                           |                           |



T0A:  Power circuits and hazards: hazardous voltages; fuses and circuit breakers; grounding; lightning protection; battery safety; electrical code compliance

T0A01: 12V is low, so 'shock' can't be the right option. Choose the safety related option.
T0A02: General knowledge
T0A03: Green wire -> ground
T0A04: fuse -> interrupt power for safety
T0A05: fuse -> interrupt power for safety
T0A06: General knowledge
T0A07: When grounding, all ground connections must be connected together
T0A08: fuse -> interrupt power for safety
T0A09: When grounding, all ground connections must be connected together
T0A10: voltage can't be reversed. Choose the safety related option.
T0A11: Choose the safety related option.

T0B01: Choose the most safe option.
T0B02: Remove grounding connections is stupid. Choose the safest option.
T0B03: Choose the most safe option.
T0B04: Choose the most safe option.
T0B05: gin pole is used to lift stuff
T0B06: Choose the most safe option.
T0B07: Choose the most safe option.
T0B08: When grounding, all ground connections must be connected together
T0B09: Monthly fee stuff is stupid. Choose the most safe option.
T0B10: Sharp bends increase the chance of arcing.
T0B11: Local rules trump general rules.
T0B12: A and B are nonsense. C is only option.
T0B13: choose the safest option.

T0C01: Learn: RF is non-ionizing, no genetic damage.
T0C02: Learn: Frequency with lowest MPE is 50MHz.
T0C03: Learn: Max power level before RF exposure evaluation is 50W PEP at antenna.
T0C04: Intuition.
T0C05: Learn: different RF frequencies, different human body absorption
T0C06: Learn: different ways to determine RF exposure compliance
T0C07: Learn: RF is non-ionizing, no genetic damage -> painful RF burn is only reasonable option.
T0C08: Antenna is what determines RF radition power at alocation, not transmitter.
T0C09: Never contact the FCC -> B is only reasonable option.
T0C10: Learn: What is duty cycle? -> Duty cycle lowers averages.
T0C11: Learn: What is duty cycle? -> Duty cycle specifies the ON time.
T0C12: Learn: RF is non-ionizing, no genetic damage 
T0C13: Learn: What is duty cycle? -> Duty cycle lowers averages.

T1A01: Learn: advancing skills in the technical and communication phases of the radio art.
T1A02: Learn: it's always the FCC.
T1A03: Learn: FCC -> English
T1A04: Learn: One license grant only
T1A05: Learn: it's always the license databases
T1A06: Learn: a beacon is used to observe propagation or related experimental activities
T1A07: Learn: space station -> 50km above the surface
T1A08: Learn: local channel and other parameters -> volunteer coordinators/amateur operators
T1A09: Learn: local channel and other parameters -> volunteer coordinators/amateur operators
T1A10: Learn: RACES -> all kinds of emergency stuff
T1A11: Learn: interference is always bad.

T1B01: Learn: ITU -> United Nations
T1B02: Learn: space stations have very low requirements to interact with.
T1B03: Learn: wavelength to freq rule: 300/6m -> 50
T1B04: Learn: wavelength to freq rule: 300/146.52 -> 2
T1B05: Learn: 219-220MHz: fixed digital message forwarding systems only
T1B06: Learn: Technician and HF always restricted to 10m.
T1B07: Learn: 50MHz and 144MHz -> CW only
T1B08: Learn: amateurs are less important than non-amateurs
T1B09: Learn: no equipment is perfect
T1B10: Learn: Technician and HF always restricted to 10m.
T1B11: Learn: HF -> max 200W
T1B12: Learn: VHF -> max 1500W

T1C01: Learn: technician, general, amateur extra
T1C02: Learn: a license is usually enough
T1C03: 
T1C04: 
T1C05: 
T1C06: 
T1C07: 
T1C08: 
T1C09: 
T1C10: 
T1C11: 
T1C12: 
T1C13: 

T1C01: 
T1C02: 
T1C03: 
T1C04: 
T1C05: 
T1C06: 
T1C07: 
T1C08: 
T1C09: 
T1C10: 
T1C11: 
T1C12: 
T1C13: 

