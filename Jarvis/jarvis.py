import speech_recognition as sr
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    print(f"[Jarvis]: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to microphone input and convert to text"""
    r = sr.Recognizer()
    try:
        # Try using PyAudio first
        try:
            with sr.Microphone() as source:
                print("🎤 Listening... (speak now)")
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
        except AttributeError:
            # PyAudio not available, inform user
            print("❌ Microphone not available. PyAudio is not installed for Python 3.14")
            print("Please use test_jarvis.py for text-based testing")
            return ""
        
        print("🔄 Processing speech...")
        command = r.recognize_google(audio).lower()
        print(f"✅ You said: {command}")
        return command
        
    except sr.WaitTimeoutError:
        print("⏱️ No speech detected, please try again")
        return ""
    except sr.UnknownValueError:
        print("❓ Could not understand audio, please speak clearly")
        return ""
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return ""
    except Exception as e:
        print(f"❌ Error: {e}")
        return ""

def jarvis():
    speak("Hello, I am Jarvis. Talk to me.")
    while True:
        command = listen()

        if "hello" in command:
            speak("Hello, nice to hear from you.")
        elif "how are you" in command:
            speak("I am functioning at full capacity.")
        elif "your name" in command:
            speak("I am Jarvis, your assistant.")
        elif "exit" in command or "quit" in command:
            speak("Goodbye!")
            break
        else:
            if command != "":
                speak("I heard you say " + command)

jarvis()