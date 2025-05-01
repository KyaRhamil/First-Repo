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

# Memory
memory = []
chat_history = []
eliza_mood = "neutral"

# Reflections
reflections = {
    "i am": "you are", "i": "you", "me": "you", "my": "your",
    "you are": "I am", "you": "me", "your": "my"
}

# Cursed words English
curse_words_english = (
    r".*\b(fuck|shit|damn|bitch|asshole)\b.*",
    [
        "Please watch your language.",
        "Let's keep our conversation respectful.",
        "Mind your words, please.",
        "I'd prefer if we stayed polite.",
        "Let's refrain from using such language."
    ]
)

# English patterns
# English patterns (updated)
english_pairs = [
    curse_words_english,  # Added curse words filter
    (r"hi|hello|hey", ["Hello! 😊", "Hi there! 👋", "Hey! How can I help?"]),
    (r"how are you?", ["I'm feeling great, thanks for asking!", "Feeling super helpful today! 💬", "All systems go! 🚀"]),
    (r"i need (.*)", ["Why do you need %1?", "Would getting %1 help you?", "What would happen if you don't get %1?"]),
    (r"i feel (.*)", ["Why do you feel %1?", "Since when have you felt %1?", "Do you often feel %1?"]),
    (r"because (.*)", ["Is that the only reason?", "Are there other reasons?", "Tell me more about that."]),
    (r"(.*) sorry (.*)", ["No problem. 🙏", "It's okay, everyone makes mistakes.", "No worries!"]),
    (r"(.*) help (.*)", ["I'm always here to help! 🛠️", "Tell me what you need.", "Sure, what do you need assistance with?"]),
    (r"i'm (.*)", ["Why are you %1?", "How long have you been %1?", "What made you %1?"]),
    (r"what is your name?", ["I'm Eliza, your chat friend! 🤖", "Call me Eliza."]),
    (r"who created you?", ["I was created by an awesome developer! 👩‍💻", "Someone smart built me!"]),
    (r"(.*) sad (.*)", ["I'm sorry you're sad. 😢 Want to talk about it?", "Sadness is tough. I'm here to listen."]),
    (r"(.*) happy (.*)", ["That's awesome! What made you happy? 🎉", "Yay! Happiness is contagious."]),
    (r"(.*)", ["Interesting. Tell me more.", "I see. Go on...", "That's intriguing."])
]

# Masamang salita Tagalog
curse_words_tagalog = (
    r".*\b(tangina|putang ina|gago|ulol|puta)\b.*",
    [
        "Pakiusap, gamitin natin ang magalang na pananalita.",
        "Iwasan natin ang pagmumura, salamat.",
        "Magalang na usapan lang sana.",
        "Tayo'y maging maayos sa salita.",
        "Huwag sanang gamitin ang mga malaswang salita."
    ]
)

# Tagalog patterns
# Tagalog patterns (updated)
tagalog_pairs = [
    curse_words_tagalog,  # Added curse words filter
    (r"kamusta.*", ["Mabuti naman ako, ikaw? 🤗", "Ayos lang ako. Kumusta ka rin?"]),
    (r"kailangan ko ng (.*)", ["Bakit mo kailangan ang %1?", "Para saan ang %1?", "Ano ang magiging epekto ng %1?"]),
    (r"nais ko na (.*)", ["Bakit mo gustong %1?", "Ano ang nararamdaman mo tungkol sa %1?", "May dahilan ba kung bakit mo hinahangad ang %1?"]),
    (r"gusto ko ng (.*)", ["Bakit mo gusto ang %1?", "Anong magagawa ng %1 sa'yo?", "Ano ang nararamdaman mo kapag iniisip mo ang %1?"]),
    (r"anong ginagawa mo.*", ["Nakikipag-chat sa'yo! 😄", "Nag-iisip ng masasayang bagay!", "Nag-aabang ng kwento mo."]),
    (r"bakit (.*)", ["Bakit mo yan naisip?", "Ano sa tingin mo ang dahilan?", "Puwede mong ikwento pa kung bakit?"]),
    (r"malungkot ako", ["Pasensya ka na. 😔 Gusto mo bang pag-usapan?", "Nandito ako para makinig.", "Minsan okay lang malungkot. Nandito lang ako."]),
    (r"masaya ako", ["Yehey! 🎉 Anong nagpapasaya sa'yo?", "Nakakatuwa naman!", "Ikwento mo pa, gusto kong marinig!"]),
    (r"sino ka?.*", ["Ako si Eliza, ang kaibigan mong chatbot. 🤖", "Ako ang chatbot na si Eliza."]),
    (r"sino ang gumawa sa'yo?.*", ["Si Ramil sa tulong ng makabagong teknolohiya.", "Dexter Basillian."]),
    (r"(.*)", ["Puwede mong ikwento pa?", "Gusto kong marinig pa yan.", "Interesante, ikwento mo pa."])
]


# Language detection with Taglish sensitivity
def detect_language(text):
    try:
        lang = langdetect.detect(text)
        if any(word in text.lower() for word in ["ikaw", "ako", "kamusta", "gusto", "sino", "malungkot", "masaya"]):
            return "tl"
        return "tl" if lang == "tl" else "en"
    except:
        return "en"

# Sticker Reactions
def sticker_reaction(text):
    stickers = {
        "happy": "🎉 Wooohoo! Saya mo ah!",
        "sad": "🤗 Yakap! Andito lang ako.",
        "angry": "😡 Relax muna tayo, okay lang magalit minsan.",
        "love": "💖 Awww, love is in the air!",
        "help": "🛟 Let's work through it together!",
        "thank": "🙏 You're welcome!"
    }
    for keyword, sticker in stickers.items():
        if keyword in text.lower():
            return sticker
    return None

# Response generation
def generate_response(text):
    if any(word in text.lower() for word in ["i feel", "i'm", "malungkot", "masaya"]):
        memory.append(text)

    if memory and random.random() < 0.2:
        past = random.choice(memory)
        return f"You mentioned before: '{past}'. How do you feel about it now?"

    lang = detect_language(text)
    pairs = english_pairs if lang == "en" else tagalog_pairs

    for pattern, responses in pairs:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            response = random.choice(responses)
            return response.replace("%1", match.group(1)) if match.lastindex else response

    return "I'm sorry, I didn't catch that. Could you repeat?"

# TTS Speak
def speak(text):
    def run_tts():
        local_engine = pyttsx3.init()

        # --- Volume Adjustment ---
        local_engine.setProperty('volume', 1.0)  

        if eliza_mood == "sad":
            local_engine.setProperty('rate', 125)
        elif eliza_mood == "happy":
            local_engine.setProperty('rate', 190)
        else:
            local_engine.setProperty('rate', 155)
            
        local_engine.say(text)
        local_engine.runAndWait()

    threading.Thread(target=run_tts, daemon=True).start()

# Typing animation
def type_response(message, response):
    sticker = sticker_reaction(message)
    chat_display.configure(state="normal")
    chat_display.insert(ctk.END, f"\nYou: {message}\n", "user")
    chat_display.insert(ctk.END, "\nEliza is typing...", "typing")
    chat_display.configure(state="disabled")
    chat_display.see(ctk.END)
    time.sleep(0.8)

    chat_display.configure(state="normal")
    chat_display.delete("typing.first", "typing.last")
    chat_display.insert(ctk.END, "Eliza: ", "eliza")
    chat_display.configure(state="disabled")
    chat_display.see(ctk.END)

    type_speed = 0.05 if eliza_mood == "sad" else 0.02 if eliza_mood == "happy" else 0.03
    for char in response:
        chat_display.configure(state="normal")
        chat_display.insert(ctk.END, char, "eliza")
        chat_display.configure(state="disabled")
        chat_display.see(ctk.END)
        time.sleep(random.uniform(type_speed, type_speed + 0.015))

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

    speak(response)

# Mood updates
def update_mood(message):
    global eliza_mood
    if any(word in message.lower() for word in ["happy", "masaya", "excited", "awesome"]):
        eliza_mood = "happy"
        app.configure(bg_color="#D0F0C0")
        mood_label.configure(text="😃")
    elif any(word in message.lower() for word in ["sad", "malungkot", "cry"]):
        eliza_mood = "sad"
        app.configure(bg_color="#D0D3D4")
        mood_label.configure(text="😢")
    elif any(word in message.lower() for word in ["angry", "galit"]):
        eliza_mood = "angry"
        app.configure(bg_color="#F08080")
        mood_label.configure(text="😡")
    else:
        eliza_mood = "neutral"
        app.configure(bg_color="#FFFFFF")
        mood_label.configure(text="😐")

# Voice input
def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        chat_display.configure(state="normal")
        chat_display.insert(ctk.END, "\n🎤 Listening...\n")
        chat_display.configure(state="disabled")
        chat_display.see(ctk.END)
        try:
            audio = r.listen(source, timeout=5)
            voice_text = r.recognize_google(audio)
            user_input.delete(0, ctk.END)
            user_input.insert(0, voice_text)
            send_message()
        except sr.UnknownValueError:
            chat_display.configure(state="normal")
            chat_display.insert(ctk.END, "Sorry, I didn’t catch that. 😕\n")
            chat_display.configure(state="disabled")
        except sr.RequestError:
            chat_display.configure(state="normal")
            chat_display.insert(ctk.END, "Speech service error. 🚫\n")
            chat_display.configure(state="disabled")
        except sr.WaitTimeoutError:
            chat_display.configure(state="normal")
            chat_display.insert(ctk.END, "No speech detected. 💤\n")
            chat_display.configure(state="disabled")

# Save chat
def save_chat():
    with open("chat_history.txt", "w", encoding="utf-8") as f:
        for line in chat_history:
            f.write(line + "\n")

# Save chat to PDF
def save_chat_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf")
    pdf.add_font("Symbola", "", "Symbola.ttf")

    margin = 15
    pdf.set_margins(left=margin, top=margin, right=margin)
    pdf.set_auto_page_break(auto=True, margin=margin)

    y = margin

    # Generate a unique filename
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    pdf_filename = f"chat_history_{timestamp}.pdf"

    for line in chat_history:
        try:
            if line.startswith("You:"):
                pdf.set_font("DejaVu", "B", 12)
                pdf.set_text_color(0, 0, 128)
                pdf.cell(0, 8, line[:4], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", "", 12)
                pdf.set_text_color(0, 0, 0)
                text_parts = line[4:].strip().split(" ")
                for part in text_parts:
                    if any(ord(char) > 1000 for char in part):
                        pdf.set_font("Symbola", "", 12)
                        pdf.cell(pdf.get_string_width(part + " "), 6, part + " ")
                    else:
                        pdf.set_font("DejaVu", "", 12)
                        pdf.cell(pdf.get_string_width(part + " "), 6, part + " ")
                pdf.ln()

            elif line.startswith("Eliza:"):
                pdf.set_font("DejaVu", "B", 12)
                pdf.set_text_color(128, 0, 0)
                pdf.cell(0, 8, line[:6], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", "", 12)
                pdf.set_text_color(0, 0, 0)
                text_parts = line[6:].strip().split(" ")
                for part in text_parts:
                    if any(ord(char) > 1000 for char in part):
                        pdf.set_font("Symbola", "", 12)
                        pdf.cell(pdf.get_string_width(part + " "), 6, part + " ")
                    else:
                        pdf.set_font("DejaVu", "", 12)
                        pdf.cell(pdf.get_string_width(part + " "), 6, part + " ")
                pdf.ln()

            else:
                pdf.set_font("DejaVu", "I", 12)
                pdf.set_text_color(0, 128, 0)
                pdf.multi_cell(0, 6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.ln(4)

        except Exception as e:
            print(f"Error formatting line: {line} - {e}")
            pdf.set_font("DejaVu", "", 12)
            pdf.set_text_color(255, 0, 0)
            pdf.multi_cell(0, 6, "Error rendering line", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(pdf_filename)  # Use the unique filename
    print(f"Chat history saved to PDF ({pdf_filename})")

# Memory wipe
def wipe_memory():
    memory.clear()
    chat_display.configure(state="normal")
    chat_display.insert(ctk.END, "\n🧹 Memory cleared.\n")
    chat_display.configure(state="disabled")

# Toggle Dark/Light mode
def toggle_mode():
    current_mode = ctk.get_appearance_mode()
    ctk.set_appearance_mode("Light" if current_mode == "Dark" else "Dark")

# GUI
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("Eliza")
app.geometry("580x750")

top_frame = ctk.CTkFrame(app)
top_frame.pack(pady=10)

mood_label = ctk.CTkLabel(top_frame, text="😐", font=("Arial", 30))
mood_label.pack(side="left", padx=10)

mode_button = ctk.CTkButton(top_frame, text="🌗 Toggle Mode", command=toggle_mode)
mode_button.pack(side="left", padx=10)

save_pdf_button = ctk.CTkButton(top_frame, text="Save as PDF", command=save_chat_pdf)
save_pdf_button.pack(side="left", padx=10)

wipe_button = ctk.CTkButton(top_frame, text="🧹 Wipe Memory", command=wipe_memory)
wipe_button.pack(side="left", padx=10)

chat_display = ctk.CTkTextbox(app, width=520, height=500, state="disabled", wrap="word", font=("Consolas", 15))
chat_display.pack(padx=20, pady=(10, 10))
chat_display.tag_config("user", foreground="#3498db")
chat_display.tag_config("eliza", foreground="#2ecc71")
chat_display.tag_config("typing", foreground="#95a5a6")


user_input = ctk.CTkEntry(app, width=400, font=("Arial", 16))
user_input.pack(padx=20, pady=10)

def send_message(event=None):
    message = user_input.get()
    if message.strip() == "":
        return
    user_input.delete(0, ctk.END)
    update_mood(message)
    response = generate_response(message)
    threading.Thread(target=type_response, args=(message, response), daemon=True).start()

button_frame = ctk.CTkFrame(app)
button_frame.pack(pady=5)

send_button = ctk.CTkButton(
    button_frame, text="📩 Send", width=140, height=50, command=send_message
)
send_button.grid(row=0, column=0, padx=10)

mic_button = ctk.CTkButton(
    button_frame, text="🎤 Speak", width=140, height=50, command=lambda: threading.Thread(target=voice_input, daemon=True).start()
)
mic_button.grid(row=0, column=1, padx=10)

app.bind('<Return>', send_message)

chat_display.configure(state="normal")
chat_display.insert(ctk.END, "👋 Greetings! I'm Eliza. How can I help you today?\n\n")
chat_display.configure(state="disabled")
chat_display.see(ctk.END)

app.protocol("WM_DELETE_WINDOW", lambda: (save_chat(), app.destroy()))
app.mainloop()

#The pdf file will be saved in the same directory as the script. But it's not currently working.
# You can uncomment the save_chat_pdf function call in the GUI section to enable it.
# The chat history will be saved in a text file named "chat_history.txt" in the same directory as the script.
# The memory wipe function will clear the memory of the chatbot.
# The toggle mode function will switch between light and dark mode for the GUI.
# The voice input function will allow the user to speak their message instead of typing it.
# The typing animation will simulate the chatbot typing its response.
# The sticker reaction function will add a sticker based on the user's mood.
# The mood update function will change the chatbot's mood based on the user's input.
# The response generation function will create a response based on the user's input and the chatbot's mood.
