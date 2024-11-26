import speech_recognition as sr
import pyttsx3
import webbrowser
import requests
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize the speech engine
engine = pyttsx3.init()

# Function to make the assistant speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen for user input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise. Please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening now...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            command = recognizer.recognize_google(audio).lower()
            return command
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand that.")
            return None
        except sr.WaitTimeoutError:
            speak("No input detected. Please try again.")
            return None

# Function to get weather updates
def get_weather(city):
    API_KEY = "your_openweather_api_key"  # Replace with your OpenWeather API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        weather_data = response.json()
        if weather_data["cod"] == 200:
            temperature = weather_data["main"]["temp"]
            description = weather_data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temperature} degrees Celsius with {description}.")
            return f"The temperature in {city} is {temperature} degrees Celsius with {description}."
        else:
            speak("Sorry, I couldn't find the weather for that location.")
            return "Weather data not found."
    except Exception as e:
        speak(f"Unable to fetch weather data. Error: {e}")
        return str(e)

# Function to set reminders
reminders = []

def set_reminder(task, time):
    reminders.append({"task": task, "time": time})
    speak(f"Reminder set for {task} at {time}.")
    return {"task": task, "time": time}

def check_reminders():
    current_time = datetime.now().strftime("%H:%M")
    for reminder in reminders:
        if reminder["time"] == current_time:
            speak(f"Reminder: {reminder['task']}")
            reminders.remove(reminder)

# Function to perform web search
def perform_web_search(query):
    speak(f"Searching the web for {query}.")
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searched for {query}."

@app.route('/run_code', methods=['POST'])
def assistant():
    """Main Assistant Endpoint."""
    data = request.json
    command = data.get("command", "").lower()

    if not command:
        return jsonify({"error": "No command provided."}), 400

    if "weather in" in command:
        city = command.split("weather in", 1)[1].strip()
        result = get_weather(city)

    elif "set a reminder" in command:
        task = data.get("task", "No task provided")
        time = data.get("time", "No time provided")
        result = set_reminder(task, time)

    elif "search for" in command or "look up" in command:
        query = command.split("search for", 1)[1].strip() if "search for" in command else command.split("look up", 1)[1].strip()
        result = perform_web_search(query)

    elif "exit" in command or "quit" in command:
        result = "Goodbye!"
        speak(result)

    else:
        result = "I'm not sure how to handle that command yet."
        speak(result)

    return jsonify({"message": result, "input": data})

app.route('/api/speak', methods=['POST'])
def api_speak():
    data = request.json
    text = data.get("text")
    speak(text)
    return jsonify({"message": "Spoken successfully!"})

@app.route('/api/listen', methods=['GET'])
def api_listen():
    result = listen()
    if result:
        return jsonify({"command": result})
    else:
        return jsonify({"error": "Could not process input"}), 400




# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

