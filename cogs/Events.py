import discord
from discord.ext import commands 

class Kgnar_message: 
    id = 363076151867867144  # Kgnar's id, only need to update it here if needs to be changed (other checks refer to class var)
    @staticmethod
    def swear_filter(msg):  # needs to have a clean msg to analyse when input
        swears = [
            'frick',
            'fuck', 
            'stupid',
            'idiot',
            'idot',
            'cunt',
            'fucking'
        ]
        for swear in swears: 
            if swear in msg: return True 
            else: pass 
        return False 
    def __init__(self, content): 
        self.content = content  # Equivalent to message parameter from Events 
        self.msg = content.content.lower().strip() # 'clean' version of the message to use in checks 
    def check_kgnar(self):  # returns true if the author of the message that created the obj is kgnar 
        return True if self.msg.author.id==self.id else False 
    def neutral_emoji_check(self): 
        if '😐' in self.msg: return "SMH STOP USING THAT EMOJI STUPID STUPID STUPID :neutral_face:"
    def grin_emoji_check(self): 
        if '😁' in self.msg: return "YOU ARE NOT FUNNY IDOT STOP SOTP SOPT SPOTSPOTPOSPO"
    def jesus_check(self): 
        if 'jesus' in self.msg: return "me (jesus) when kgnar mentions my name :rolling_eyes::rolling_eyes::rolling_eyes:"
    def lake_tahoe(self):
        if 'tahoe' in self.msg: return "ewwww kgnar hometown?????? :nauseated_face:"
    def ew(self): 
        if "🤨" in self.msg: return ":face_with_raised_eyebrow:kgnar spoke:face_with_raised_eyebrow:, must get her manager <@360392861608574978>"
    def no(self):
        if "no" in self.msg and "furry" in self.msg: return "bad furry. :rolling_eyes:"
        elif "no" in self.msg: return "bad kgnar. :thumbsdown: :thumbsdown: :thumbsdown: :thumbsdown: :thumbsdown: :thumbsdown: "
    def asked(self):
        if "😡" in self.msg: return "nobody asked though :rofl: :rofl: :rofl:"
    def roll(self):
        if "🙄" in self.msg: return "kgnar is misbehaving again, I apologize for this incident. please contact her manager"
    def cry(self):
        if "😭" in self.msg: return ":joy::joy::joy::joy::joy:"
    def yawn(self):
        if "🥱" in self.msg: return "shut up"
    def swear(self): 
        if Kgnar_message.swear_filter(self.msg): return "STOP SWEARING KGNAR YOU DON'T HAVE HUMAN RIGHTS :rage:"
    def welcome(self):
        if "welcome" in self.msg or " hi " in self.msg: return """Hello, I'm kgnar, my current goal in BTE is to completely build the entire SLT (South Lake Tahoe) area (and possibly further).
Having grown up in SLT, I've had a lot of time to familiarize the area's land/structures and specific details which make them unique. 
While I no longer live in Tahoe, I'm able to visit often and hold a sense of nostalgia which provides motivation to continue the project. 
On top of my area's knowledge, I have been an active player of Minecraft for nearly 8 years; giving me lots of experience on the game's building techniques. 
Overall, I believe my experience could help to finish another area on the map and I would enjoy being a part of the community. 
Thank you for taking the time to review my application.""" 
    kgnar_functions_list = [ # Holds all the functions that we'll loop through, don't forget to add a function here after implementing it
        neutral_emoji_check, 
        grin_emoji_check, 
        jesus_check, 
        lake_tahoe,
        ew,
        no,
        asked,
        roll,
        cry,
        yawn,
        swear, 
        welcome
    ]

class Events(commands.Cog): 
    def __init__(self, bot): 
        self.client = bot 
    
    @commands.Cog.listener()
    async def on_message(self, message): 
        if message.author == self.client.user: return # ignore messages from the bot 

        if message.author.id == Kgnar_message.id: # if we enter here, kgnar has sent a message   
            # creating obj 
            kgnar = Kgnar_message(message)
            # now checking if our functions are met and responding accordingly 
            for function in kgnar.kgnar_functions_list: # accessing function list of the kgnar obj, could also be the kgnar class 
                response = function(kgnar) # Running the function passing the kgnar obj cause self is not implicit in this case 
                if response: 
                    await message.channel.send(response) 
                else:
                    pass # if response is none, just continue looping and/or finish the process 

def setup(bot):
    bot.add_cog(Events(bot))