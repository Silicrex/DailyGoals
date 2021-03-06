import random


def get_welcome(current_welcome=None):
    if current_welcome is None:
        return "Welcome! I hope you have a great and productive experience with the program!"
    if current_welcome != "Welcome!!" and random.randint(1, 10) == 1:  # 10% chance, no consecutive reroll
        return "Welcome!!"

    welcome_messages = [
        "WELCOME! HOW IS YOUR DAY GOING?",
        "EAT YOUR FRUITS AND VEGGIES!!",
        "STAY HYDRATED!!!!",
        "THESE WERE NOT TYPED WITH CAPS LOCK, I HOLD LEFT SHIFT",
        "POSTURE CHECK!",
        "WHY DO PEOPLE SAY VIOLETS ARE BLUE? THEY'RE VIOLET! GOOGLE IT IF YOU DON'T KNOW!!!",
        "I FEEL LIKE I SHOULD HAVE BEEN TRACKING THE DEVELOPMENT OF THIS ON GITHUB LOL. HMM..",
        "THE ORIGINAL WELCOME MESSAGES FELT TOO CHEESY TO ME, SO I REPLACED THEM WITH RAMBLINGS",
        "DO YOU LIKE FRENCH TOAST? WHAT ABOUT CREPES? BELGIAN WAFFLES? I CALLED THOSE 'BELGIUM WAFFLES' FOR A WHILE.",
        "HOW DO YOU FEEL ABOUT COMPETITIVE PROGRAMMING?",
        "HOW'S THE WEATHER?",
        "CHOCOLATE OR VANILLA ICE CREAM? I LIKE VANILLA-CHOCOLATE SWIRLED SOFT-SERVED!!",
        "HAVE YOU EVER MADE YOUR OWN DISCORD BOT? GOT ANY IDEAS?",
        "IF YOU USE THIS TO ACHIEVE GOOD, PRODUCTIVE GOALS, I SALUTE YOU AND AM PROUD!",
        "TRY TO SPEND AT LEAST A GOOD 3 HOURS ON CHALLENGING EXERCISE PER WEEK!",
        "HAVE YOU MADE YOUR OWN GAME BEFORE? GOT ANY IDEAS?",
        "SETTING REGULAR GOALS IS A GREAT WAY TO ENCOURAGE CONSISTENCY!",
        "DO YOU LIKE READING BOOKS? IF SO; ANY BOOKS YOU'RE LOOKING FORWARD TO RIGHT NOW?",
        "KEEP YOUR EQUIPMENT CLEAN!",
        "MAKE SURE YOU GET ENOUGH SLEEP!",
        "I CHALLENGE YOU TO SPECIFICALLY TRY ENCOURAGING SOMEBODY TODAY!!",
        "DON'T PROCRASTINATE!",
        "QUICK! WHAT'S 13 SQUARED?",
        "ANY LANGUAGES YOU WANT TO LEARN/PROGRESS WITH; PROGRAMMING OR OTHERWISE? IF SO, HOW'S THAT GOING?",
        "ANY MUSICAL INSTRUMENTS YOU WANT TO LEARN/PROGRESS WITH? IF SO, HOW'S THAT GOING?",
        "QUICK! WHAT'S 27 * 12 WITHOUT USING A CALCULATOR?",
        "OKAY, SORRY, WRITING THESE WELCOME MESSAGES IS A LOT HARDER THAN I ANTICIPATED. HERE; YOU THINK OF ONE!"
        "CREATIVE EXERCISE!",
        "HAVE ANY GOOD PLANS AFTER FINISHING YOUR GOALS TODAY? IF SO, USE THAT AS MOTIVATION TO FINISH THEM FIRST!",
        "WELCOME! HAVE A GOOD DAY!",
        "ANYONE YOU'VE BEEN MEANING TO TALK TO?",
        "QUICK! WHAT'S THE 13TH LETTER OF THE ALPHABET?",
        "GREETINGS!",
        "BONJOUR!",
        "HI!!!",
        "WHY HELLO THERE!",
        "HOLA!",
        "PLAY ANY GAMES LATELY? IF SO, WHAT'S BEEN YOUR FAVORITE?",
        "ALOHA!",
    ]
    if current_welcome in welcome_messages:
        welcome_messages.remove(current_welcome)  # No consecutive reroll of same message!
    return random.choice(welcome_messages)
