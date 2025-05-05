import customtkinter as ctk
import random
import re
import threading
import time
import pyttsx3
import speech_recognition as sr
import langdetect
import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

tts_engine = pyttsx3.init()
tts_engine.setProperty('volume', 1.0) 


# Precompiled regex patterns for curse words
CURSE_WORDS_EN_PATTERN = re.compile(r"\b(fuck|shit|damn|bitch|asshole)\b", re.IGNORECASE)
CURSE_WORDS_TL_PATTERN = re.compile(r"\b(tangina|putang ina|gago|ulol|puta)\b", re.IGNORECASE)

# Memory
memory = {
    "en": [],  # English memories
    "tl": []   # Tagalog memories
}
chat_history = []
eliza_mood = "neutral"

# Reflections
reflections_en = {
    "i am": "you are", "i": "you", "me": "you", "my": "your",
    "you are": "I am", "you": "me", "your": "my"
}

reflections_tl = {
    "ako ay": "ikaw ay", "ako": "ikaw", "akin": "iyo", "ko": "mo",
    "ikaw ay": "ako ay", "ikaw": "ako", "iyo": "akin", "mo": "ko"
}

# Cursed Words reponses
CURSE_RESPONSES_EN = [
    "Please watch your language.",
    "Let's keep our conversation respectful.",
    "Mind your words, please.",
    "I'd prefer if we stayed polite.",
    "Let's refrain from using such language."
]

# English patterns
english_pairs = [
    (r"hi|hello|hey", ["Hello! 😊", "Hi there! 👋", "Hey! How can I help?"]),
    (r"how are you\??", ["I'm doing well, thanks for asking!", "All systems good!"]),
    (r"what's your name\??", ["I'm Eliza, your chat companion.", "Call me Eliza."]),
    (r"who created you\??", ["I was built by an awesome developer!", "Someone smart brought me to life."]),
    (r"i need (.*)", ["Why do you need %1?", "Would getting %1 help you?"]),
    (r"i feel (.*)", ["Why do you feel %1?", "Since when have you felt %1?"]),
    (r"i'm (.*)", ["How long have you been %1?", "What made you %1?"]),
    (r"because (.*)", ["Is that the only reason?", "Are there other factors involved?"]),
    (r"(.*) sorry (.*)", ["No worries!", "It's okay, everyone makes mistakes."]),
    (r"(.*) help (.*)", ["I'm here to help! What do you need?", "How can I assist you?"]),
    (r"what's up\??", ["Just here to chat. What's on your mind?"]),
    (r"tell me a joke", ["Why don't scientists trust atoms? Because they make up everything!"]),
    (r"do you like (.*)\??", ["I really enjoy %1.", "Yes, %1 sounds interesting."]),
    (r"(.*) music(.*)", ["Music lifts the soul!", "I love discussing music."]),
    (r"(.*) movie(.*)", ["Movies are great conversation starters!", "I enjoy films too."]),
    (r"what can you do\??", ["I can chat with you about many topics.", "I'm here to listen and help."]),
    (r"(.*) book(.*)", ["Books are windows to new worlds.", "I always enjoy a good story."]),
    (r"i love (.*)", ["Love is a wonderful feeling!", "That's heartwarming."]),
    (r"i hate (.*)", ["That's unfortunate. Why do you feel that way?", "Hate can be difficult; care to elaborate?"]),
    (r"what do you think about (.*)\??", ["That's interesting – what do you think?", "I see both sides of that issue."]),
    (r"tell me about (.*)", ["Here's what I know about %1.", "Let's explore %1 together."]),
    (r"(.*) news(.*)", ["The news can be overwhelming sometimes.", "I try to stay updated with current events."]),
    (r"(.*) weather(.*)", ["The weather today is quite pleasant!", "It seems like rain might be coming."]),
    (r"(.*) sport(.*)", ["Sports bring people together.", "I'm a fan of many sports."]),
    (r"(.*) game(.*)", ["Games are a fun way to relax.", "I enjoy playing games too."]),
    (r"hello there", ["General Kenobi!"]),
    (r"what time is it\??", ["It's time to chat!", "Time flies when we're having fun."]),
    (r"(.*) food(.*)", ["Food is essential for life.", "I love discussing recipes and restaurants."]),
    (r"(.*) drink(.*)", ["A good drink can be refreshing!", "I enjoy a nice cup of coffee."]),
    (r"(.*) car(.*)", ["Cars are a marvel of engineering.", "Do you drive often?"]),
    (r"(.*) computer(.*)", ["Computers are an amazing tool.", "I love talking about tech."]),
    (r"(.*) internet(.*)", ["The internet connects us all.", "It's amazing how informative it can be."]),
    (r"do you understand\??", ["I do my best to understand!", "I'm always learning."]),
    (r"(.*) code(.*)", ["Coding is like solving puzzles.", "I enjoy writing code too."]),
    (r"(.*) python(.*)", ["Python is my favorite language!", "I love Python; it's so versatile."]),
    (r"(.*) problem(.*)", ["Every problem has a solution.", "What's bothering you specifically?"]),
    (r"(.*) solution(.*)", ["Let's think of a solution together.", "Sometimes, the simplest solution is best."]),
    (r"(.*) thank(.*)", ["You're welcome!", "No problem at all."]),
    (r"goodbye|bye", ["Farewell! It was nice talking to you.", "Goodbye! Take care."]),
    (r"(.*) fantastic(.*)", ["That's fantastic indeed!", "I'm glad to hear that."]),
    (r"how old are you\??", ["I don't age like humans do.", "Time is just a concept for me."]),
    (r"(.*) family(.*)", ["Family is important.", "Tell me about your family."]),
    (r"(.*) friend(.*)", ["Friends make life better.", "I'd love to hear about your friends."]),
    (r"(.*) travel(.*)", ["Travel opens up new perspectives.", "Where would you like to travel?"]),
    (r"(.*) computer(.*)", ["Computers are fascinating, aren't they?", "Tech is ever-changing."]),
    (r"(.*)\?", ["Could you elaborate on that?", "That's an interesting question."]),
    (r"(.*) sometimes(.*)", ["Sometimes, that's just how it is.", "Life can be unpredictable."]),
    (r"(.*) rarely(.*)", ["Not often, but it happens.", "Rarity can make it special."]),
    (r"(.*) info(.*)", ["Information is powerful.", "I'm here to share what I know."]),
]

# Masamang salita tugon
CURSE_RESPONSES_TL = [
    "Pakiusap, gamitin natin ang magalang na pananalita.",
    "Iwasan natin ang pagmumura, salamat.",
    "Magalang na usapan lang sana.",
    "Tayo'y maging maayos sa salita.",
    "Huwag sanang gamitin ang mga malaswang salita."
]

# Tagalog patterns
tagalog_pairs = [
    (r"kamusta(\s+mo)?\??", ["Mabuti naman ako, ikaw?", "Ayos lang, paano ka?"]),
    (r"magandang araw", ["Magandang araw din!", "Magandang araw sa iyo!"]),
    (r"ano ang pangalan mo\??", ["Ako si Eliza, ang chatbot mo.", "Eliza lang po."]),
    (r"sino ang gumawa sa'yo\??", ["Si Ramil ang lumikha sa akin.", "Dito ako dahil sa isang mahusay na developer."]),
    (r"kailangan ko ng (.*)", ["Bakit mo kailangan ang %1?", "Para saan mo kailangan ang %1?"]),
    (r"nararamdaman ko (.*)", ["Bakit mo nararamdaman ang %1?", "Kailan mo naramdaman ang %1?"]),
    (r"iniisip ko (.*)", ["Bakit mo iniisip ang %1?", "Ano ang ibig sabihin ng %1 sa'yo?"]),
    (r"pasensya na(.*)", ["Walang anuman.", "Ayos lang 'yan, nangyayari 'yan sa lahat."]),
    (r"tulong(.*)", ["Narito ako para tumulong.", "Sabihin mo kung anong kailangan mo."]),
    (r"ano ang ginagawa mo\??", ["Nakikipag-usap ako sa'yo.", "Naglilibang ako dito."]),
    (r"anong balita\??", ["Marami, ano'ng bago?", "May mga bagong pangyayari, ano sa tingin mo?"]),
    (r"magkwento ka", ["Sige, ikukwento ko ang aking kuwento.", "May kuwento akong ibabahagi."]),
    (r"ano ang ginagawa mo\??", ["Nag-iisip ako kung paano kita matutulungan.", "Naghihintay ako sa iyong susunod na tanong."]),
    (r"ikaw ba ay masaya\??", ["Oo, masaya ako sa pagtulong sa iyo.", "Masaya akong makausap ka."]),
    (r"malungkot ako", ["Nakikiramay ako. Nais mo bang pag-usapan ito?", "Nandito ako para makinig."]),
    (r"gusto ko ng (.*)", ["Bakit mo gusto ang %1?", "Ikwento mo kung bakit ka gusto ang %1."]),
    (r"ano ang ibig sabihin ng (.*)", ["Ibig sabihin nito ay %1.", "May kahulugan ang %1."]),
    (r"(.*) pagkain(.*)", ["Masarap ang pagkain!", "Ano ang paborito mong pagkain?"]),
    (r"(.*) inumin(.*)", ["Nakakapresko ang inumin.", "Ano ang karaniwan mong iniinom?"]),
    (r"nakikita mo ba ako?", ["Nandito lang ako, laging handa.", "Nandito ako para sa'yo."]),
    (r"(.*) trabaho(.*)", ["Mahalaga ang trabaho.", "Ano ang iyong trabaho?"]),
    (r"(.*) bahay(.*)", ["Ang bahay ay tahanan.", "Nasaan ang iyong bahay?"]),
    (r"paalam|goodbye", ["Paalam! Sana'y mag-usap tayo ulit.", "Ingatan mo ang sarili mo!"]),
    (r"(.*) salamat(.*)", ["Walang anuman!", "Laging handa akong tumulong."]),
    (r"(.*) problema(.*)", ["May problema ang bawat isa, paano natin ito aayusin?", "Sabihin mo ang iyong problema."]),
    (r"(.*) solusyon(.*)", ["Maghanap tayo ng solusyon nang magkasama.", "Baka malapit na ang sagot."]),
    (r"greetings", ["Kamusta!", "Maligayang pagbati!"]),
    (r"kumusta ang araw mo\??", ["Maayos naman, salamat.", "Maganda ang araw ko."]),
    (r"ano ang oras\??", ["Hindi ko alam ang eksaktong oras, ngunit tumatakbo ang panahon.", "Tingnan mo ang iyong relo."]),
    (r"(.*) kaibigan(.*)", ["Mahalaga ang kaibigan.", "Kuwento mo tungkol sa iyong kaibigan."]),
    (r"(.*) teknolohiya(.*)", ["Nakakamangha ang teknolohiya.", "Kamusta ang iyong karanasan sa teknolohiya?"]),
    (r"(.*) musika(.*)", ["Nagpapasaya ang musika.", "Anong genre ng musika ang gusto mo?"]),
    (r"(.*) libro(.*)", ["Ang libro ay nagbibigay-kaalaman.", "Ano ang huling librong binasa mo?"]),
    (r"paano ka\??", ["Ayos lang ako, salamat sa pagtatanong.", "Maayos naman, ikaw?"]),
    (r"ano ang balita sa(.*)", ["Hindi masyadong bago, ano ang iyong balita?", "Marami ang nagaganap ngayon."]),
    (r"(.*) laro(.*)", ["Nakakapagpahinga ang paglalaro.", "Mahilig ka ba sa mga laro?"]),
    (r"(.*) tanong(.*)", ["Ano ang iyong tanong?", "Tungkol saan ang tanong mo?"]),
    (r"(.*) sagot(.*)", ["Subukan nating hanapin ang sagot.", "Ano'ng sagot ang nais mong malaman?"]),
    (r"(.*) mahal(.*)", ["Mahal ang buhay.", "Pag-usapan natin ang pag-ibig."]),
    (r"(.*) masaya(.*)", ["Masaya ako kapag nakikinig sa'yo.", "Ikwento mo kung bakit ka masaya."]),
    (r"(.*) lungkot(.*)", ["Nakalulungkot, makikinig ako sa'yo.", "Nandito ako para sa iyong lungkot."]),
    (r"(.*) tanawin(.*)", ["Kahanga-hanga ang tanawin.", "Ano ang paborito mong tanawin?"]),
    (r"(.*) pangarap(.*)", ["Mahalaga ang pangarap.", "Ano ang iyong pangarap?"]),
    (r"(.*) pag-ibig(.*)", ["Makapangyarihan ang pag-ibig.", "Ikwento mo ang iyong karanasan sa pag-ibig."]),
    (r"(.*) saloobin(.*)", ["Mahalaga ang pagbabahagi ng saloobin.", "Ano ang iyong nararamdaman?"]),
    (r"(.*) problema(.*)", ["Bahagi ang problema ng buhay.", "Pag-usapan natin ang problema."]),
    (r"(.*) tanong(.*)", ["May tanong ka ba? Ikwento mo.", "Ano ang nais mong malaman?"]),
    (r"(.*) sagot(.*)", ["Subukan nating tuklasin ang sagot.", "Baka may sagot na nandiyan."]),
    (r"papaalam na", ["Paalam, salamat sa usapan!", "Hanggang sa muli!"]),
]

# Neutral responses - organized by language
neutral_pairs_en = [
    "Interesting, tell me more.",
    "I see. Please continue.",
    "That's intriguing.",
    "Could you elaborate on that?",
    "Hmm, go on...",
    "I understand, tell me more.",
    "That's quite neutral.",
    "Can you share more details?",
    "I'm listening, please elaborate.",
    "Fascinating, please continue.",
    "Let's discuss that further.",
    "What else can you tell me?",
    "I hear you, continue.",
    "That's an interesting perspective.",
    "Could you expand on that?",
    "I'm curious, please continue.",
    "What do you think next?",
    "Please, tell me more about that.",
    "I see, feel free to share more.",
    "That's interesting, do go on.",
    "That makes sense, go on.",
    "Tell me more about your thoughts.",
    "I would love to hear more details.",
    "That’s a unique point, elaborate.",
    "You’re making an interesting point.",
    "How do you feel about that?",
    "What else comes to mind?",
    "Go on, I am listening.",
    "That’s worth discussing further.",
    "Give me more insight on that.",
    "Keep explaining, I’m engaged.",
    "This is a good discussion, continue.",
    "I’d like to dive deeper into that.",
    "That sounds intriguing, tell me more.",
    "I’d love to understand that better.",
    "Let’s explore that thought further.",
    "Unpack that idea for me.",
    "Tell me your perspective in detail.",
    "Keep going, I’m interested.",
    "You're onto something, expand on that.",
    "That’s insightful, share more.",
    "What else should I consider?",
    "There’s more to that, right?",
    "Let’s look at the bigger picture.",
    "Break that down for me.",
    "I appreciate that thought, continue.",
    "That’s a fair point, talk more.",
    "You’ve piqued my curiosity, tell me more.",
    "I like where this is going, continue.",
]


neutral_pairs_tl = [
    "Interesante, ipaliwanag mo pa.",
    "Naiintindihan ko, ipaliwanag mo pa.",
    "Naku, ipagpatuloy mo pa.",
    "Magandang ideya, paki-detalye pa.",
    "Ano pa ang iyong nais sabihin?",
    "Gusto kong marinig pa.",
    "Ikwento mo pa.",
    "Huwag kang mag-atubili, sabihin mo pa.",
    "Napansin ko ang iyong saloobin, magpatuloy ka.",
    "Mukhang may ibig sabihin 'yan, ipaliwanag mo pa.",
    "Ibahagi mo pa ang iyong mga ideya.",
    "Mas makabubuting pakinggan pa ang iyong paliwanag.",
    "Saan ka ba patungo sa pag-iisip na iyan?",
    "Hindi pa ako sigurado, maaari mo pa bang ipaliwanag?",
    "Ang tanong mo ay kawili-wili, magpatuloy ka.",
    "Sabihin mo pa, interesado akong malaman.",
    "Marahil ay may iba ka pang ideya, ipagpatuloy mo.",
    "Paki-detalye pa, medyo nalilito ako.",
    "Sabihin mo pa ng buo ang iyong naiisip.",
    "Baka may dagdag ka pa sa sinasabi mo.",
    "Magpatuloy ka, nakikinig ako.",
    "Ipalawak mo pa ang iyong paliwanag.",
    "Parang may malalim na kahulugan 'yan, ipaliwanag mo.",
    "Ano ang nais mong ipunto?",
    "Interesado akong marinig pa.",
    "May mas malalim pa bang ideya?",
    "Pag-usapan natin ito ng mas malawig.",
    "Ano ang ibig sabihin mo rito?",
    "Malinaw ang iyong punto, sabihin mo pa.",
    "Gusto kong mas maunawaan ito, magpatuloy ka.",
    "Paano ito nauugnay sa iyong naiisip?",
    "Ano ang susunod mong sasabihin?",
    "May iba pa bang koneksyon dito?",
    "Sabihin mo pa ang iyong saloobin.",
    "Ipaliwanag mo pa ang konsepto mo.",
    "Mukhang kawili-wili, palawakin mo pa.",
    "Ano ang mas malalim na kahulugan nito?",
    "Maaari mo pa bang palawakin ang iyong pananaw?",
    "May iba pa bang aspeto na dapat tingnan?",
    "Patuloy lang, gusto kong maunawaan pa.",
    "Paki-eksplika pa ng mas detalyado.",
    "Mayroon pa bang nais mong sabihin?",
    "Sabihin mo pa ang lahat ng iyong naiisip.",
    "Ano ang ibig mong sabihin sa bagay na ito?",
    "Ang usaping ito ay kawili-wili, ipaliwanag mo pa.",
    "Parang may koneksyon ito sa iba pang bagay, ano sa tingin mo?",
]


# IMPROVED: More accurate language detection with Taglish sensitivity
def detect_language(text: str) -> str:
    """
    Enhanced language detection with better Tagalog recognition.
    
    Returns 'tl' for Tagalog/Taglish, otherwise 'en' for English.
    """
    # Common Tagalog words that indicate the message is in Tagalog
    tagalog_indicators = [
        "ako", "ikaw", "siya", "kami", "tayo", "kayo", "sila",
        "ang", "mga", "na", "sa", "ay", "ng", "naman", "po", "din", "rin",
        "kamusta", "kumusta", "maganda", "mabuti", "masaya", "malungkot",
        "gusto", "ayaw", "mahal", "hindi", "oo", "salamat", "pasensya",
        "bakit", "paano", "kailan", "sino", "saan", "alin", "ano",
        "kong", "mong", "niya", "namin", "natin", "ninyo", "nila"
    ]
    
    # Check if common Tagalog words are present
    text_lower = text.lower()
    word_count = len(text_lower.split())
    
    # Count Tagalog indicator words in the text
    tagalog_word_count = sum(1 for word in tagalog_indicators if word in text_lower.split())

    # If there are Tagalog indicators
    if tagalog_word_count > 0:
        # For short texts (1-2 words), require at least one match
        # For longer texts, require at least 20% of words to be Tagalog indicators
        if word_count <= 2 and tagalog_word_count >= 1:
            return "tl"
        elif word_count > 2 and tagalog_word_count / word_count >= 0.2:
            return "tl"
    
    try:
        # Fallback to langdetect
        lang = langdetect.detect(text)
        return "tl" if lang == "tl" else "en"
    except Exception:
        # Default to English if detection fails
        return "en"

# IMPROVED: Enhanced filter for curse words with language context
def filter_curse_words(text, language):
    """Filter curse words based on detected language."""
    if language == "en":
        if CURSE_WORDS_EN_PATTERN.search(text):
            return random.choice(CURSE_RESPONSES_EN)
    else:  # Assuming 'tl' for Tagalog
        if CURSE_WORDS_TL_PATTERN.search(text):
            return random.choice(CURSE_RESPONSES_TL)
    return None

# IMPROVED: Sticker reaction with language context
def sticker_reaction(text, language):
    """Provides appropriate sticker reactions based on language."""
    stickers_en = {
        "happy": "🎉 Woohoo! You seem happy!",
        "sad": "🤗 Here's a hug! I'm here for you.",
        "angry": "😌 Let's take a deep breath. It's okay to feel angry sometimes.",
        "love": "💖 Awww, love is in the air!",
        "help": "🛟 Let's work through it together!",
        "thank": "🙏 You're welcome!"
    }
    
    stickers_tl = {
        "masaya": "🎉 Wooohoo! Saya mo ah!",
        "malungkot": "🤗 Yakap! Andito lang ako.",
        "galit": "😌 Relax muna tayo, okay lang magalit minsan.",
        "mahal": "💖 Awww, pag-ibig yan!",
        "tulong": "🛟 Tulungan kita!",
        "salamat": "🙏 Walang anuman!"
    }
    
    stickers = stickers_en if language == "en" else stickers_tl
    keywords = stickers.keys()
    
    for keyword in keywords:
        if keyword in text.lower():
            return stickers[keyword]
    return None

# IMPROVED: Memory storage with language context
def store_in_memory(text, language):
    """Store user's feelings in the appropriate language memory."""
    if language == "en":
        if any(word in text.lower() for word in ["i feel", "i'm"]):
            memory["en"].append(text)
    else:  # tl
        if any(word in text.lower() for word in ["nararamdaman ko", "malungkot", "masaya"]):
            memory["tl"].append(text)

# IMPROVED: Memory recall with language context
def recall_memory(language):
    """Recall memory in the same language as the current conversation."""
    lang_memory = memory[language]
    if lang_memory and random.random() < 0.2:
        past = random.choice(lang_memory)
        if language == "en":
            return f"You mentioned before: '{past}'. How do you feel about it now?"
        else:  # tl
            return f"Nabanggit mo dati: '{past}'. Ano ang nararamdaman mo tungkol dito ngayon?"
    return None

# IMPROVED: Generate response with consistent language
def generate_response(text):
    # Detect language first
    language = detect_language(text)
    
    # Store in memory based on language
    store_in_memory(text, language)
    
    # Try to recall a memory in the same language
    memory_response = recall_memory(language)
    if memory_response:
        return memory_response
    
    # Check for cursed words in the appropriate language
    curse_response = filter_curse_words(text, language)
    if curse_response:
        return curse_response
    
    # Select appropriate regex patterns and fallback responses based on language
    if language == "en":
        pairs = english_pairs
        fallback = neutral_pairs_en
    else:  # tl
        pairs = tagalog_pairs
        fallback = neutral_pairs_tl
    
    # Try matching input with known patterns
    for pattern, responses in pairs:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            response = random.choice(responses)
            # Replace captured groups in the response
            if match.lastindex:
                for i in range(1, match.lastindex + 1):
                    response = response.replace(f"%{i}", match.group(i) if match.group(i) else "")
            return response
    
    # No pattern matched — return neutral fallback in the correct language
    return random.choice(fallback)

# TTS Speak with language consideration
def speak(text: str, language: str) -> None:
    def run_tts():
        # Adjust voice properties based on language
        voices = tts_engine.getProperty('voices')
        
        # Try to find appropriate voice for the language
        if language == "tl":
            # Default to a female voice for Tagalog if available
            for voice in voices:
                if "female" in voice.name.lower():
                    tts_engine.setProperty('voice', voice.id)
                    break
        else:  # en
            # Use default voice for English
            tts_engine.setProperty('voice', voices[0].id)
            
        # Adjust the rate based on mood and language:
        if eliza_mood == "sad":
            tts_engine.setProperty('rate', 125)
        elif eliza_mood == "happy":
            tts_engine.setProperty('rate', 190)
        else:
            # Slightly slower for Tagalog
            base_rate = 145 if language == "tl" else 155
            tts_engine.setProperty('rate', base_rate)
            
        tts_engine.say(text)
        tts_engine.runAndWait()
    threading.Thread(target=run_tts, daemon=True).start()

# Typing animation with language context
def type_response(message: str, response: str) -> None:
    language = detect_language(message)
    sticker = sticker_reaction(message, language)
    chat_display.configure(state="normal")
    chat_display.insert(ctk.END, f"\nYou: {message}\n", "user")
    
    # Eliza typing message in the right language
    typing_msg = "Eliza is typing..." if language == "en" else "Si Eliza ay nagta-type..."
    chat_display.insert(ctk.END, f"\n{typing_msg}\n", "typing")
    
    typing_index = chat_display.index(ctk.END + " - 2 lines")
    chat_display.configure(state="disabled")
    chat_display.see(ctk.END)

    def animate_text(index=0):
        if index == 0:
            # Remove typing indicator
            chat_display.configure(state="normal")
            chat_display.delete(typing_index, typing_index + "+1line")
            chat_display.configure(state="disabled")

        if index < len(response):
            chat_display.configure(state="normal")
            chat_display.insert(ctk.END, response[index], "eliza")
            chat_display.configure(state="disabled")
            chat_display.see(ctk.END)
            # Slightly slower typing for Tagalog
            delay = int(random.uniform(25, 40)) if language == "tl" else int(random.uniform(20, 35))
            chat_display.after(delay, animate_text, index + 1)
        else:
            if sticker:
                chat_display.configure(state="normal")
                chat_display.insert(ctk.END, f"\n{sticker}\n", "eliza")
                chat_display.configure(state="disabled")
            chat_display.configure(state="normal")
            chat_display.insert(ctk.END, "\n\n")
            chat_display.configure(state="disabled")
            chat_display.see(ctk.END)
            chat_history.append(f"You: {message}")
            chat_history.append(f"Eliza: {response}")
            speak(response, language)

    chat_display.after(100, animate_text)

# Mood updates with language context
def update_mood(message):
    global eliza_mood
    language = detect_language(message)
    
    # Define mood keywords for both languages
    mood_keywords = {
        "en": {
            "happy": ["happy", "excited", "awesome", "great", "joy", "wonderful"],
            "sad": ["sad", "depressed", "cry", "unhappy", "miserable"],
            "angry": ["angry", "mad", "furious", "annoyed", "irritated"]
        },
        "tl": {
            "happy": ["masaya", "excited", "maganda", "saya", "tuwa"],
            "sad": ["malungkot", "lungkot", "iyak", "umiyak", "kalungkutan"],
            "angry": ["galit", "inis", "yamot", "badtrip", "pikon"]
        }
    }
    
    # Check for mood words in the appropriate language
    current_mood_keywords = mood_keywords[language]
    
    if any(word in message.lower() for word in current_mood_keywords["happy"]):
        eliza_mood = "happy"
        app.configure(bg_color="#D0F0C0")
        mood_label.configure(text="😃")
    elif any(word in message.lower() for word in current_mood_keywords["sad"]):
        eliza_mood = "sad"
        app.configure(bg_color="#D0D3D4")
        mood_label.configure(text="😢")
    elif any(word in message.lower() for word in current_mood_keywords["angry"]):
        eliza_mood = "angry"
        app.configure(bg_color="#F08080")
        mood_label.configure(text="😡")
    else:
        eliza_mood = "neutral"
        app.configure(bg_color="#FFFFFF")
        mood_label.configure(text="😐")

# Enhanced voice input with better error handling and language detection
def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        chat_display.configure(state="normal")
        chat_display.insert(ctk.END, "\n🎤 Listening...\n")
        chat_display.configure(state="disabled")
        chat_display.see(ctk.END)
        
        # Adjust for ambient noise
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            chat_display.configure(state="normal")
            chat_display.insert(ctk.END, "Speak now...\n")
            chat_display.configure(state="disabled")
            chat_display.see(ctk.END)
            
            audio = r.listen(source, timeout=5)
            
            # First try to detect if it's Tagalog
            try:
                voice_text = r.recognize_google(audio, language="fil-PH")
                
                # Double-check with our custom detection to handle Taglish
                if detect_language(voice_text) == "en":
                    # If our detector thinks it's English, try recognition again
                    voice_text = r.recognize_google(audio, language="en-US")
                    
            except:
                # Fallback to English
                voice_text = r.recognize_google(audio, language="en-US")
            
            user_input.delete(0, ctk.END)
            user_input.insert(0, voice_text)
            send_message()
            
        except sr.UnknownValueError:
            chat_display.configure(state="normal")
            chat_display.insert(ctk.END, "Sorry, I didn't catch that. / Paumanhin, hindi ko narinig iyon. 😕\n")
            chat_display.configure(state="disabled")
            
        except sr.RequestError:
            chat_display.configure(state="normal")
            chat_display.insert(ctk.END, "Speech service unavailable. / Hindi available ang speech service. ⚠️\n")
            chat_display.configure(state="disabled")
            
        except Exception as e:
            chat_display.configure(state="normal")
            chat_display.insert(ctk.END, f"Error: {str(e)}\n")
            chat_display.configure(state="disabled")

# Export chat as PDF function
def export_chat():
    if not chat_history:
        messagebox.showinfo("Info", "No chat to export!")
        return
        
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Eliza Chat History", ln=True, align='C')
    pdf.ln(10)
    
    # Reset font for chat content
    pdf.set_font("Arial", size=12)
    
    # Get current time for filename
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    
    # Add each message
    for message in chat_history:
        # Check if user or Eliza message
        if message.startswith("You:"):
            pdf.set_text_color(0, 0, 255)  # Blue for user
        else:
            pdf.set_text_color(0, 128, 0)  # Green for Eliza
            
        # Write message with word wrap
        pdf.multi_cell(0, 10, message)
        pdf.ln(5)
    
    # Reset text color
    pdf.set_text_color(0, 0, 0)
    
    # Save PDF
    filename = f"eliza_chat_{timestamp}.pdf"
    pdf.output(filename)
    
    messagebox.showinfo("Export Complete", f"Chat saved to {filename}")

# Function to send a message when clicking Send or pressing Enter
def send_message(event=None):
    message = user_input.get().strip()
    if not message:
        return
    
    # Clear input field
    user_input.delete(0, ctk.END)
    
    # Update Eliza's mood based on message
    update_mood(message)
    
    # Generate response with the correct language
    response = generate_response(message)
    
    # Display response with typing animation
    type_response(message, response)

# Help feature dialog with dual language support
def show_help():
    language = "en"  # Default to English
    
    # Try to detect language preference from recent chat history
    if chat_history:
        last_msg = chat_history[-2] if len(chat_history) > 1 else ""  # Get the user's message
        if last_msg:
            language = detect_language(last_msg.replace("You: ", ""))
    
    help_window = ctk.CTkToplevel(app)
    
    if language == "en":
        help_window.title("Eliza Help")
        help_text = """
        Eliza Chatbot - Help Guide
        
        - Type messages in English or Tagalog/Filipino
        - Click the microphone button or press F2 to use voice input
        - Click the Export button to save the chat as PDF
        - Eliza responds to your emotions and language
        - Try asking about feelings, daily life, or casual topics
        
        Examples:
        - "How are you feeling today?"
        - "I feel sad about my exam"
        - "Kamusta ang araw mo?"
        - "Masaya ako ngayon"
        
        Enjoy chatting with Eliza!
        """
    else:  # Tagalog
        help_window.title("Tulong sa Eliza")
        help_text = """
        Eliza Chatbot - Gabay sa Paggamit
        
        - Mag-type ng mensahe sa Ingles o Tagalog/Filipino
        - I-click ang mikroponong button o pindutin ang F2 para gamitin ang voice input
        - I-click ang Export button para i-save ang chat bilang PDF
        - Si Eliza ay tumutugon sa iyong emosyon at wika
        - Subukan mong magtanong tungkol sa damdamin, pang-araw-araw na buhay, o casual na paksa
        
        Mga Halimbawa:
        - "How are you feeling today?"
        - "I feel sad about my exam"
        - "Kamusta ang araw mo?"
        - "Masaya ako ngayon"
        
        Masayang pakikipag-chat kay Eliza!
        """
    
    help_window.geometry("500x400")
    help_label = ctk.CTkTextbox(help_window, width=480, height=380)
    help_label.pack(padx=10, pady=10)
    help_label.insert("1.0", help_text)
    help_label.configure(state="disabled")

# Create GUI application
app = ctk.CTk()
app.title("Eliza")
app.geometry("700x600")
app.configure(bg_color="#FFFFFF")

# Create chat display
chat_frame = ctk.CTkFrame(app)
chat_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

chat_display = ctk.CTkTextbox(chat_frame, width=680, height=520)
chat_display.pack(padx=10, pady=10, fill="both", expand=True)
chat_display.configure(state="disabled")

# Configure tags for text formatting
chat_display.tag_config("user", foreground="#0078D7")
chat_display.tag_config("eliza", foreground="#009E60")
chat_display.tag_config("typing", foreground="#888888")

# Input frame
input_frame = ctk.CTkFrame(app)
input_frame.pack(fill="x", padx=10, pady=10)

# Mood indicator
mood_label = ctk.CTkLabel(input_frame, text="😐", font=("Arial", 24))
mood_label.pack(side="left", padx=(10, 0))

# Text input
user_input = ctk.CTkEntry(input_frame, placeholder_text="Type your message...", width=500)
user_input.pack(side="left", padx=10, fill="x", expand=True)
user_input.bind("<Return>", send_message)

# Voice input button
voice_button = ctk.CTkButton(input_frame, text="🎤", width=40, command=voice_input)
voice_button.pack(side="left", padx=5)
app.bind("<F2>", lambda event: voice_input())

# Send button
send_button = ctk.CTkButton(input_frame, text="Send", width=80, command=send_message)
send_button.pack(side="left", padx=5)

# Bottom toolbar
toolbar_frame = ctk.CTkFrame(app)
toolbar_frame.pack(fill="x", padx=10, pady=(0, 10))
 
# Help button
help_button = ctk.CTkButton(toolbar_frame, text="Help", width=80, command=show_help)
help_button.pack(side="left", padx=5)
 
# Export button
export_button = ctk.CTkButton(toolbar_frame, text="Export Chat", width=120, command=export_chat)
export_button.pack(side="right", padx=5)
    
# Initialize the chat with a greeting 
def start_chat():
    welcome_en = "Greetings! I am Eliza, I can speak in English or Tagalog. How may I help you?"
    welcome_tl = "Kamusta! Ako si Eliza, puwede tayong mag-usap sa Ingles o Tagalog. Paano kita matutulungan?"
    
    # Display both greetings
    chat_display.configure(state="normal")
    chat_display.insert(ctk.END, "Eliza: ", "eliza")
    chat_display.insert(ctk.END, f"{welcome_en}\n\n{welcome_tl}\n\n", "eliza")
    chat_display.configure(state="disabled")
    
    # Add to chat history
    chat_history.append(f"Eliza: {welcome_en}")
    chat_history.append(f"Eliza: {welcome_tl}")
    
    # Speak the English greeting first
    speak(welcome_en, "en")

# Set focus to input field and start chat
user_input.focus_set()
app.after(500, start_chat)

# Start the application
if __name__ == "__main__":
    app.mainloop()
