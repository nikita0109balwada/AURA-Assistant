AURA: AI Voice Assistant with GUI

**AURA** is a sleek AI voice/text assistant application built using Python, CustomTkinter, and Groq LLM. It supports natural language understanding, speech recognition, text-to-speech, image analysis, and weather reporting, all wrapped in a beautiful dark/light mode GUI.

✨ Features

* 🎧 Voice interaction via microphone (Google Speech Recognition)
* 🌟 AI-powered chat using \[Groq API] (LLama3-based models)
* 👤 User-friendly GUI with theme switching (dark/light)
* 🌦️ Live weather updates by city (OpenWeather API)
* 📅 Real-time clock and time labeling on messages
* 📷 Image upload and analysis using BLIP
* 📚 PDF export of AI responses
* 📃 Side menu with chat history, save, and theme toggle options

---

🚀 Getting Started

Prerequisites

* Python 3.10+
* API Keys:

  * `GROQ_API_KEY` for Groq AI
  * `REPLICATE_API_TOKEN` for image captioning/generation
  * `OPEN_WEATHER_API_KEY` for weather info

Installation

bash
# Clone this repository
git clone https://github.com/nikita0109balwada/AURA-Assistant.git
cd AURA-Assistant

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install required packages
pip install -r requirements.txt


### Run the App

bash
python Main.py

---

📂 Project Structure
.
├── Main.py              # Main GUI logic (CustomTkinter + Backend Integration)
├── backend.py           # Core AI, speech, image, and utility functions
├── icons/               # Light/Dark mode icon sets
├── fonts/               # Custom fonts used in the GUI
├── settings.json        # Stores user theme preferences
├── .env                 # Stores API keys (GROQ, Replicate, OpenWeather)




🔧 Tech Stack

* **Frontend:** Python + CustomTkinter
* **AI Backend:** Groq LLM (LLama 3)
* **Speech:** Google Speech Recognition + gTTS
* **Image Captioning:** Replicate + Salesforce BLIP
* **Weather API:** OpenWeatherMap

---
🚀 Planned Features

* 🔹 Drag & drop for images
* 🔹 Voice wake word ("Hey Aura")
* 🔹 More advanced weather visuals (icons, forecasts)
* 🔹 Real-time translation between languages

---

💼 License

This project is open-source under the MIT License. Feel free to fork, modify, and contribute.

---

👨‍💻 Author

Made with ❤️ by [Nikita](# AURA: AI Voice Assistant with GUI





✨ Acknowledgments

* [Groq](https://groq.com/)
* [Replicate](https://replicate.com/)
* [OpenWeather](https://openweathermap.org/)
* [Google Speech Recognition](https://pypi.org/project/SpeechRecognition/)
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
