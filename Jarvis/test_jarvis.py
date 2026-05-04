import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()
    print(f"[JARVIS]: {text}")

def listen():
    """Simulated listen function - returns user input instead of microphone"""
    command = input("You: ").lower()
    print(f"[Recognized]: {command}")
    return command

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

if __name__ == "__main__":
    jarvis()
