import customtkinter as ctk
from PIL import Image
import time
import threading
import tkinter.font as tkfont
import json
import os
import datetime  
import requests
from PIL import Image
from dotenv import load_dotenv
import backend
import tkinter as tk

load_dotenv()

OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")

# === App Theme Settings ===
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

# Initialize global message counter
message_counter = 0  

class CityInputPopup(ctk.CTkToplevel):
    def __init__(self, parent, on_submit_callback):
        super().__init__(parent)
        self.title("Change City")
        self.geometry("300x160")
        self.resizable(False, False)
        self.grab_set()  # Modal window

        self.label = ctk.CTkLabel(self, text="Enter City Name:")
        self.label.pack(pady=(20, 10))

        self.entry = ctk.CTkEntry(self, width=200)
        self.entry.pack(pady=(0, 10))
        self.entry.focus()

        self.submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit)
        self.submit_btn.pack()

        self.callback = on_submit_callback

    def submit(self):
        city = self.entry.get().strip()
        if city:
            self.callback(city)
        self.destroy()

class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, text, is_user=False):
        super().__init__(master, fg_color="#f0f0f0" if ctk.get_appearance_mode() == "Light" else "#333333", corner_radius=20)
        self.grid_columnconfigure(0, weight=1)
        self.is_user = is_user
        self._last_width = 0  # Initialize for tracking width

        text_color = "#333333" if ctk.get_appearance_mode() == "Light" else "#f0f0f0"

        self.inner_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.inner_frame.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="nsew")

        self.label = ctk.CTkLabel(self.inner_frame, text=text, text_color=text_color,
                                  justify="right" if is_user else "left", anchor="w", wraplength=500)
        self.label.grid(row=0, column=0, sticky="w")

        time_color = "#777777" if ctk.get_appearance_mode() == "Light" else "#aaaaaa"
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.time_label = ctk.CTkLabel(self, text=current_time, text_color=time_color, font=ctk.CTkFont(size=10))
        self.time_label.grid(row=1, column=0, sticky="e" if is_user else "w", padx=10, pady=(0, 6))
        self.time_label.is_time = True

        if is_user:
            self.configure(fg_color="#e0f7fa" if ctk.get_appearance_mode() == "Light" else "#26a69a")
            self.label.configure(text_color="#000000" if ctk.get_appearance_mode() == "Light" else "#ffffff")

        self.after(10, self.update_bubble_width)  # Let layout settle before measuring


    def update_bubble_width(self):
        self.label.update_idletasks()

        required_width = self.label.winfo_reqwidth() + 20
        max_width = self.master.winfo_width() - 60  # Some padding
        final_width = min(required_width, max_width)

        if abs(self._last_width - final_width) > 1:
            self._last_width = final_width
            self.configure(width=final_width)
            self.inner_frame.configure(width=final_width - 12)


# Updated display_message function
def display_message(message, sender):
    global message_counter

    if not message.strip():
        return

    is_user = (sender == "user")
    bubble = ChatBubble(output_box, message, is_user=is_user)

    if is_user:
        bubble.grid(row=message_counter, column=1, padx=(40, 10), pady=5, sticky="se")
    else:
        bubble.grid(row=message_counter, column=0, padx=(10, 40), pady=5, sticky="sw")

    message_counter += 1

    # Scroll to bottom after slight delay
    output_box.after(50, lambda: output_box._parent_canvas.yview_moveto(1.0))

# === Initialize App ===
app = ctk.CTk()
app.geometry("700x550")
app.title("AURA")
icon_image = tk.PhotoImage(file="icon.png")  # PNG works here
app.iconphoto(True, icon_image)  # True = affects the root window
app.resizable(False , False)  

is_listening = False

def toggle_listening():
    global is_listening

    if not is_listening:
        is_listening = True
        backend.speak_enabled = True

        display_message("🎙️ Listening activated. Say something!", "assistant")
        backend.speak_text("Listening activated. Say something!", lang='en')

        def listen_loop():
            while is_listening:
                recorded_text = backend.record_audio()

                if recorded_text:
                    display_message(recorded_text, "user")
                    lang_code = backend.detect_language(recorded_text)
                    main_response, follow_up = backend.get_ai_response(recorded_text, lang_code)

                    # Speak ONLY, don't show text
                    if main_response:
                        backend.speak_text(main_response, lang_code)

                    if follow_up:
                        backend.speak_text(follow_up, lang_code)

                else:
                    backend.speak_text("Sorry, I didn't catch that.", lang='en')

        threading.Thread(target=listen_loop, daemon=True).start()

    else:
        is_listening = False
        backend.speak_enabled = False
        display_message("Listening stopped.", "assistant")
        backend.speak_text("Listening stopped.", lang='en')


# === Load Custom Font ===

def register_ttf_fonts(font_dir="fonts"):
    for font_file in os.listdir(font_dir):
        if font_file.lower().endswith(".ttf"):
            font_path = os.path.join(font_dir, font_file)
            try:
                tkfont.Font(file=font_path)  # Triggers registration
                
            except Exception as e:
                print(f"Error registering font {font_file}: {e}")


def load_custom_fonts(app, font_dir="fonts"):
    loaded_fonts = {}

    # Get system-available font families
    available_fonts = tkfont.families()

    # List of desired custom fonts (you can expand this list)
    desired_fonts = {
        "STEELAR": 22,
        "Aquire": 26,
        "DAGGERSQUARE": 20,
        "Enter Sansman": 24,
        "NCL Monster Beast Demo": 24,
        "Planet Space": 24,
        "Squares Bold": 24,
        "Digital Cards Demo": 26,
        "Swera Demo": 32,
    }

    for font_name, font_size in desired_fonts.items():
        try:
            if font_name in available_fonts:
                loaded_fonts[font_name] = ctk.CTkFont(family=font_name, size=font_size)
                
            else:
                print(f"⚠️ Font '{font_name}' not found. Using fallback 'Arial'")
                loaded_fonts[font_name] = ctk.CTkFont(family="Arial", size=font_size)
        except Exception as e:
            
            loaded_fonts[font_name] = ctk.CTkFont(family="Arial", size=font_size)

    return loaded_fonts


try:
    custom_font_name = "STEELAR"  # Use the actual font family name
    custom_font_size = 22
    if custom_font_name in tkfont.families():
        custom_font = ctk.CTkFont(family=custom_font_name, size=custom_font_size)
        print(f"Loaded custom font: {custom_font_name}")
    else:
        print(f"Custom font '{custom_font_name}' not found. Using fallback.")
        custom_font_name = "Arial"
        custom_font = ctk.CTkFont(family=custom_font_name, size=custom_font_size)
except Exception as e:
    print(f"Error loading font: {e}. Using fallback.")
    custom_font_name = "Arial"
    custom_font_size = 26
    custom_font = ctk.CTkFont(family=custom_font_name, size=custom_font_size)

register_ttf_fonts("fonts")
fonts = load_custom_fonts(app)


# --- Theme Definitions ---
light_theme = {
    "primary": "#6200EE",
    "primary_variant": "#3700B3",
    "secondary": "#03DAC6",
    "secondary_variant": "#018786",
    "background": "#F0F0F0",
    "surface": "#FFFFFF",
    "surface_variant": "#E0E0E0",
    "error": "#B00020",
    "on_primary": "#FFFFFF",
    "on_secondary": "#000000",
    "on_background": "#000000",
    "on_surface": "#000000",
    "on_error": "#FFFFFF",
    "visualizer_bar": "#018786",
    "progress_bar": "#3700B3",
    "textbox_fg": "#FFFFFF",
    "textbox_text": "#000000",
    "entry_fg": "#E0E0E0",
    "entry_text": "#000000",
    "placeholder": "#757575",
    "clock_text": "#000000",
    "label_text": "#000000",
    "transparent_hover": "#D0D0D0"
}

dark_theme = {
    "primary": "#BB86FC",
    "primary_variant": "#9e47f5",
    "secondary": "#03DAC6",
    "secondary_variant": "#00A090",
    "background": "#121212",
    "surface": "#1E1E1E",
    "surface_variant": "#2C2C2C",
    "error": "#CF6679",
    "on_primary": "#000000",
    "on_secondary": "#000000",
    "on_background": "#FFFFFF",
    "on_surface": "#E0E0E0",
    "on_error": "#000000",
    "visualizer_bar": "#03DAC6",
    "progress_bar": "#BB86FC",
    "textbox_fg": "#2C2C2C",
    "textbox_text": "#E0E0E0",
    "entry_fg": "#2C2C2C",
    "entry_text": "#E0E0E0",
    "placeholder": "#888888",
    "clock_text": "#FFFFFF",
    "label_text": "#FFFFFF",
    "transparent_hover": "#4A4A4A"  # Darker hover for transparent buttons
}

# --- Theme Management ---
SETTINGS_FILE = "settings.json"


def save_theme_preference(theme_name):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"theme": theme_name}, f)
    except Exception as e:
        print(f"Error saving theme preference: {e}")


def load_theme_preference():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                return settings.get("theme", "dark")
        except Exception as e:
            print(f"Error loading theme preference: {e}")
            return "dark"
    return "dark"


# --- Load Icons ---
icons = {}
icon_size_button = (28, 28)
icon_size_submit = (20, 20)
weather_icon_size = (100,100)
icon_paths = {
    "mic": ("icons/light/mic.png", "icons/dark/mic.png"),
    "power": ("icons/light/power.png", "icons/dark/power.png"),
    "image": ("icons/light/image.png", "icons/dark/image.png"),
    "submit": ("icons/light/submit.png", "icons/dark/submit.png"),
    "save": ("icons/light/save.png", "icons/dark/save.png"),
    "history": ("icons/light/history.png", "icons/dark/history.png"),
    "exit": ("icons/light/exit.png", "icons/dark/exit.png"),
    "theme": ("icons/light/theme.png", "icons/dark/theme.png"),
    "collapse": ("icons/light/collapse.png", "icons/dark/collapse.png"),
    "clock": ("icons/light/clock.png", "icons/dark/clock.png"),
    "weather": ("icons/light/weather.png", "icons/dark/weather.png"),
    "location": ("icons/light/location.png", "icons/dark/location.png"),
}

# Ensure icons directory exists
if not os.path.exists("icons"):
    os.makedirs("icons/light")
    os.makedirs("icons/dark")
    print("Created 'icons/light' and 'icons/dark' directories. Please place your icon files there.")

# Load CTkImage objects
for name, (light_path, dark_path) in icon_paths.items():
    try:
        # Check if files exist before opening
        if not os.path.exists(light_path):
            print(f"Warning: Light icon not found at {light_path}")
            light_img = None
        else:
            light_img = Image.open(light_path)

        if not os.path.exists(dark_path):
            print(f"Warning: Dark icon not found at {dark_path}")
            dark_img = None
        else:
            dark_img = Image.open(dark_path)

        # Handle cases where one or both images might be missing
        if light_img or dark_img:
            size = icon_size_submit if name == "submit" else icon_size_button
            icons[name] = ctk.CTkImage(light_image=light_img, dark_image=dark_img, size=size)
        else:
            print(f"Error: Could not load any image for icon '{name}'.")
            icons[name] = None  # Placeholder

    except Exception as e:
        print(f"An unexpected error occurred loading icon '{name}': {e}")
        icons[name] = None


# === Functions ===
def submit_message(event=None):
    message = command_entry.get()
    if not message.strip():
        return

    display_message(message, "user")
    command_entry.delete(0, ctk.END)

    # Run response in background thread
    threading.Thread(target=process_message, args=(message,), daemon=True).start()

def process_message(message):
    lang_code = backend.detect_language(message)
    intent_data = backend.detect_intent(message)
    intent = intent_data.get("intent")
    query = intent_data.get("query")

    if intent == "save_previous":
        if backend.last_generated_text:
            backend.save_pdf_dialog(backend.last_generated_text, lang=lang_code)
        else:
            display_message("No previous response to save.", "assistant")

    elif intent in ["chat", "chat_and_save"]:
        main_response, follow_up = backend.get_ai_response(query, lang_code)

        if main_response:
            display_message(main_response, "assistant")
        if follow_up:
            display_message(follow_up, "assistant")

        if intent == "chat_and_save" and main_response:
            backend.save_pdf_dialog(main_response, lang=lang_code)

    elif intent == "image_generation":
        backend.handle_image_generation(query)


def image_upload():
    backend.get_image_description()


def power_action():
    app.quit()  # Close GUI


def save_chat():
    if backend.last_generated_text:
        backend.save_pdf_dialog(backend.last_generated_text)
    else:
        print("No recent chat to save.")


def chat_history():
    history = backend.conversation_history

    if not history:
        display_message("No chat history available yet.", "assistant")
        return

    display_message("📜 Chat History:", "assistant")
    
    # Show last 5 entries
    for item in history[-5:]:
        sender = item["sender"]
        text = item["text"]
        display_message(text, sender)



# === Apply Theme Function ===
def apply_theme(theme_dict):
    # Configure frames
    main_frame.configure(fg_color=theme_dict["surface"])
    top_left_box.configure(fg_color=theme_dict["surface"])
    top_right_box.configure(fg_color=theme_dict["surface_variant"])
    output_frame.configure(fg_color=theme_dict["surface_variant"])
    tools_panel.configure(fg_color=theme_dict["surface_variant"])  # Configure tools_panel
    left_bottom_panel.configure(fg_color=theme_dict["surface_variant"])
    right_bottom_panel.configure(fg_color=theme_dict["surface_variant"])
    if side_menu:  # Check if side_menu exists
        side_menu.configure(fg_color=theme_dict["surface"])

    # Configure text elements
    clock_label.configure(text_color=theme_dict["clock_text"])
    name_label.configure(text_color=theme_dict["primary"])
    output_label.configure(text_color=theme_dict["label_text"])

    # Configure interactive elements
    output_box.configure(
        fg_color=theme_dict["textbox_fg"],
        border_color=theme_dict["surface_variant"]
    )

    # Apply theme to the widgets inside the scrollable frame.
    for child in output_box.winfo_children():
        if isinstance(child, ChatBubble):  # Only target ChatBubble instances.
            if child.is_user:
                child.configure(fg_color=theme_dict["primary"])  # User bubble color
                child.label.configure(text_color=theme_dict["on_secondary"])
            else:
                child.configure(fg_color=theme_dict["primary"])  # AI bubble color
                child.label.configure(text_color=theme_dict["on_secondary"])
            child.time_label.configure(text_color=theme_dict["on_secondary"])

    command_entry.configure(
        fg_color=theme_dict["entry_fg"],
        text_color=theme_dict["entry_text"],
        border_color=theme_dict["surface_variant"],
        placeholder_text_color=theme_dict["placeholder"]
    )

  
    themed_button_list = [
        tools_btn,  # Tools button gets theme color
        btn_submit,  # Submit button gets theme color
        save_icon_btn, history_icon_btn, close_icon_btn,  # Side menu buttons
        theme_toggle_btn, collapse_icon_btn  # Other themed buttons
    ]
    for btn in themed_button_list:
        if btn:  # Check if button exists
            hover_c = theme_dict["error"] if btn == close_icon_btn else theme_dict["primary_variant"]
            fg_c = theme_dict["primary"]

            btn.configure(
                fg_color=fg_c,
                hover_color=hover_c
            )
            # Set text color specifically if the button has text
            if btn.cget("text"):
                btn.configure(text_color=theme_dict["on_primary"])

    # --- Configure TRANSPARENT buttons hover color separately ---
    transparent_hover_color = theme_dict["transparent_hover"]  # Use theme-defined hover
    for btn in [btn_image, btn_mic, btn_power]:
        if btn:
            # Only configure hover_color here, leave fg_color as transparent
            btn.configure(hover_color=transparent_hover_color)



# === Toggle Theme Function ===
def toggle_theme():
    global current_theme, current_theme_dict
    if current_theme == "dark":
        new_mode = "light"
        new_theme_dict = light_theme
    else:
        new_mode = "dark"
        new_theme_dict = dark_theme

    current_theme = new_mode
    current_theme_dict = new_theme_dict
    ctk.set_appearance_mode(current_theme)
    apply_theme(current_theme_dict)
    save_theme_preference(current_theme)



# === Load Initial Theme ===
current_theme = load_theme_preference()
current_theme_dict = light_theme if current_theme == "light" else dark_theme
ctk.set_appearance_mode(current_theme)

# === GUI Layout ===

# --- Main Frame ---
main_frame = ctk.CTkFrame(app, width=700, height=550, corner_radius=0, border_width=0)
main_frame.place(x=0, y=0)

# --- Top Right Box  ---
top_right_box = ctk.CTkFrame(main_frame, width=390, height=50, corner_radius=16)
top_right_box.place(x=300, y=10)
clock_label = ctk.CTkLabel(top_right_box, text="00:00", font=("Aerial", 20), )
clock_label.place(relx=0.16, rely=0.5, anchor="center")

# -- Weather Frame inside your top_right_box --
weather_frame = ctk.CTkFrame(top_right_box, fg_color="transparent", bg_color="transparent", corner_radius=30, width=280, height=100)
weather_frame.place(relx=0.6, rely=0.97, anchor="center")  # Center it properly

# --- 1. Weather Icon ---
weather_icon = ctk.CTkLabel(weather_frame, text="", image=icons.get("weather"))
weather_icon.place(x=10, y=10)  # Just some margin from left

# --- 2. Temperature Label ---
temperature_label = ctk.CTkLabel(weather_frame, text="40°C", font=ctk.CTkFont(size=28))
temperature_label.place(x=50, y=10)  # Manually set x after icon

# --- 3. Right side frame (for Condition + Location + Humidity) ---
weather_right_frame = ctk.CTkFrame(weather_frame, fg_color="transparent", bg_color="transparent", corner_radius=20, width=170, height=100)
weather_right_frame.place(x = 130, y=15)  # Right of temperature

# --- First Row: Condition Label ---
condition_label = ctk.CTkLabel(weather_right_frame, text="Sunny", font=ctk.CTkFont(size=14))
condition_label.place(x=0, y=-8)

# --- Second Row: Humidity Label ---
humidity_label = ctk.CTkLabel(weather_right_frame, text="Humidity 10%", bg_color="transparent", font=ctk.CTkFont(size=14))
humidity_label.place(x=0, y=10)

def change_location():
    def update_city(city_name):
        global city
        city = city_name
        update_weather()  # refresh weather info
        display_message(f"📍 Location changed to: {city}", "assistant")

    CityInputPopup(app, on_submit_callback=update_city)


# Location Button (Clickable)
location_button = ctk.CTkButton(weather_right_frame, image= icons.get("location"), text="", width=8, height=8,
                                fg_color="transparent", hover_color="gray", bg_color="transparent", command=change_location)
location_button.place(x = 100, y=-4,)



def update_weather():
    try:
        api_key = os.getenv("OPEN_WEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("main"):
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"].capitalize()
            humidity = data["main"]["humidity"]

            # 🔁 Update all labels
            temperature_label.configure(text=f"{int(temp)}°C")
            condition_label.configure(text=desc)
            humidity_label.configure(text=f"Humidity: {humidity}%")
    
        else:
            temperature_label.configure(text="--°C")
            condition_label.configure(text="Not found")
            humidity_label.configure(text="--")
    

    except Exception as e:
        print(f"Weather error: {e}")
        temperature_label.configure(text="Error")
        condition_label.configure(text="Error")
        humidity_label.configure(text="--")
        
    




# Clock Icon
clock_icon_label = ctk.CTkLabel(top_right_box, image=icons.get("clock"), text="", width=32)
clock_icon_label.place(relx=0.055, rely=0.5, anchor="center")


# --- Top Left Box (Clock) ---
top_left_box = ctk.CTkFrame(main_frame, width=200, height=50, corner_radius=16)
top_left_box.place(x=10, y=10)
name_label = ctk.CTkLabel(top_left_box, text="AURA", font=fonts["Digital Cards Demo"], )
name_label.place(relx=0.5, rely=0.5, anchor="center")

# --- Output Area ---
output_frame = ctk.CTkFrame(main_frame, width=685, height=410, corner_radius=16)
output_frame.place(x=10, y=65)  # Position below top boxes
output_label = ctk.CTkLabel(output_frame, text="RESULTS", font=fonts["Aquire"])
output_label.place(relx=0.03, rely=0.028, anchor='w')
output_box = ctk.CTkScrollableFrame(output_frame, width=640, height=355, corner_radius=10, border_width=1)
output_box.place(relx=0.5, rely=0.52, anchor='center')

# Configure column weights for output_box
output_box.grid_columnconfigure(0, weight=1)
output_box.grid_columnconfigure(1, weight=1)


# === Bottom Panels ===
bottom_panel_height = 60
bottom_panel_y = 480  # Adjusted Y position slightly
panel_spacing = 5
app_padding = 10

# --- Define widths ---
tools_panel_width = 65
left_panel_width = 165
remaining_width = 700 - (app_padding * 2) - tools_panel_width - left_panel_width - (panel_spacing * 2)
right_panel_width = remaining_width  # Should be 440

# --- Tools Panel (Far Left) ---
tools_panel = ctk.CTkFrame(main_frame, width=tools_panel_width, height=bottom_panel_height, corner_radius=16)
tools_panel.place(x=app_padding, y=bottom_panel_y)

# --- Left Bottom Panel (Image, Power, Mic) ---
left_panel_x = app_padding + tools_panel_width + panel_spacing
left_bottom_panel = ctk.CTkFrame(main_frame, width=left_panel_width, height=bottom_panel_height, corner_radius=16)
left_bottom_panel.place(x=left_panel_x, y=bottom_panel_y)

# --- Right Bottom Panel (Entry, Submit) ---
right_panel_x = left_panel_x + left_panel_width + panel_spacing
right_bottom_panel = ctk.CTkFrame(main_frame, width=right_panel_width, height=bottom_panel_height, corner_radius=16)
right_bottom_panel.place(x=right_panel_x, y=bottom_panel_y)

# === Bottom Panel Widgets ===

# --- Tools Button (in tools_panel) ---
tools_btn = ctk.CTkButton(tools_panel,  # PARENT: tools_panel
                          text="☰", width=45, height=40,
                          font=("Arial", 18), corner_radius=10,
                          command=lambda: toggle_side_menu())  # Updated command
tools_btn.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

# --- Input Buttons (in left_bottom_panel) ---
# transparent_hover_color is set dynamically in apply_theme
button_y_in_panel = 10
button_x_padding = 10

# Place Image button
current_x = button_x_padding
btn_image = ctk.CTkButton(left_bottom_panel,  # PARENT: left_bottom_panel
                          image=icons.get("image"), text="", width=40, height=40,
                          fg_color="transparent",  # <<< SET TRANSPARENT HERE
                          hover=True,  # Disable default hover color (we set it manually)
                          corner_radius=10, command=image_upload)
btn_image.place(x=current_x, y=button_y_in_panel)

# Place Power button next to Image
current_x += 40 + button_x_padding
btn_power = ctk.CTkButton(left_bottom_panel,  # PARENT: left_bottom_panel
                          image=icons.get("power"), text="", width=40, height=40,
                          fg_color="transparent", 
                          hover=True,  # Disable default hover color
                          corner_radius=10, command=power_action)
btn_power.place(x=current_x, y=button_y_in_panel)

# Place Mic button next to Power
current_x += 40 + button_x_padding
btn_mic = ctk.CTkButton(left_bottom_panel,  # PARENT: left_bottom_panel
                        image=icons.get("mic"), text="", width=40, height=40,
                        fg_color="transparent",  # <<< SET TRANSPARENT HERE
                        hover=True,  # Disable default hover color
                        corner_radius=10, command = toggle_listening)
btn_mic.place(x=current_x, y=button_y_in_panel)


# --- Command Entry (in right_bottom_panel) ---
entry_x = 10
submit_button_width = 40
submit_button_x_padding = 10
entry_width = right_panel_width - entry_x - submit_button_width - (submit_button_x_padding * 2)

command_entry = ctk.CTkEntry(right_bottom_panel,  # PARENT: right_bottom_panel
                            placeholder_text="Type your message...",
                            width=entry_width,
                            height=40,
                            corner_radius=10, border_width=1)
command_entry.place(x=entry_x, y=button_y_in_panel)
command_entry.bind("<Return>", submit_message)  # Bind Enter key

# --- Submit Button (in right_bottom_panel) ---
submit_x = right_panel_width - submit_button_width - submit_button_x_padding
btn_submit = ctk.CTkButton(right_bottom_panel,  # PARENT: right_bottom_panel
                           image=icons.get("submit"), text="", width=submit_button_width, height=40,
                           fg_color="transparent",  # <<< SET TRANSPARENT HERE
                           corner_radius=10, command=submit_message)
btn_submit.place(x=submit_x, y=button_y_in_panel)


# === Side Menu (Initially hidden) ===
side_menu_width = 70
side_menu_visible = False
side_menu = ctk.CTkFrame(main_frame, width=0, height=app.winfo_reqheight(), corner_radius=0, border_width=0)
# Place it initially off-screen to the left or with 0 width at x=0
side_menu.place(x=-1, y=0, relheight=1)

# --- Side Menu Buttons ---
button_y_start = 20
button_spacing = 60
button_x = 10  # Center buttons horizontally

save_icon_btn = ctk.CTkButton(side_menu, image=icons.get("save"), text="", width=38, height=40,
                             corner_radius=10, command=save_chat)
save_icon_btn.place(x=button_x, y=button_y_start)

history_icon_btn = ctk.CTkButton(side_menu, image=icons.get("history"), text="", width=38, height=40,
                                 corner_radius=10, command=chat_history)
history_icon_btn.place(x=button_x, y=button_y_start + button_spacing)

theme_toggle_btn = ctk.CTkButton(side_menu, image=icons.get("theme"), text="", width=38, height=40,
                                  corner_radius=10, command=toggle_theme)
theme_toggle_btn.place(x=button_x, y=button_y_start + 2 * button_spacing)

close_icon_btn = ctk.CTkButton(side_menu, image=icons.get("exit"), text="", width=38, height=40,
                               corner_radius=10, command=app.quit)
close_icon_btn.place(x=button_x, y=button_y_start + 3 * button_spacing)



# --- ADD THE COLLAPSE BUTTON ---
collapse_content = icons.get("collapse") if icons.get("collapse") else "←"
collapse_text = "" if icons.get("collapse") else collapse_content
collapse_image = icons.get("collapse")

collapse_icon_btn = ctk.CTkButton(side_menu,
                                  image=collapse_image,
                                  text=collapse_text,
                                  font=("Arial", 18),
                                  width=40, height=40,
                                  corner_radius=10,
                                  fg_color="transparent",
                                  command=lambda: toggle_side_menu())  # Command to close menu
# Place it near the bottom-left of the side menu
collapse_icon_btn.place(relx=0.49, rely=0.962, anchor='s')  # Position relative to bottom


# === Menu Animation ===
animation_steps = 10
animation_delay = 10

def animate_side_menu(target_width):
    current_width = side_menu.winfo_width()

    # Avoid division by zero or unnecessary animation if already at target
    if animation_steps <= 0:
        side_menu.configure(width=int(target_width))
        if target_width == 0:
            side_menu.lower()
        else:
            side_menu.lift()
        return

    # If already at the target width, just ensure lift/lower state is correct
    if current_width == target_width:
        if target_width == 0:
            side_menu.lower()
        else:
            side_menu.lift()
        return  # Exit if no animation needed

    step_size = (target_width - current_width) / animation_steps

    def step_animation(step=0):
        # Calculate the new width for this step
        new_width = current_width + step_size * (step + 1)

        # Determine if the animation should continue based on direction
        continue_animation = False
        if step_size > 0:  # Opening
            if new_width < target_width:
                continue_animation = True
        else:  # Closing
            if new_width > target_width:
                continue_animation = True

        # Ensure we don't exceed the number of steps
        if step >= animation_steps:
            continue_animation = False

        if continue_animation:
            side_menu.configure(width=int(new_width))
            app.after(animation_delay, step_animation, step + 1)
        else:
            # Animation finished or overshot, set final width and state
            side_menu.configure(width=int(target_width))
            if target_width == 0:
                side_menu.lower()  # Lower when fully closed


    # --- Action before starting steps ---
    if target_width > 0:  # If opening animation is intended
        side_menu.lift()  # <<< CRITICAL: Lift unconditionally before starting to open

    # Start the animation steps
    step_animation()


# Ensure the toggle function remains the same
def toggle_side_menu():
    global side_menu_visible
    if side_menu_visible:
        animate_side_menu(0)  # Animate closing
    else:
        animate_side_menu(side_menu_width)  # Animate opening
    side_menu_visible = not side_menu_visible



# === Clock Update ===
def update_clock():
    now = datetime.datetime.now().strftime("%H:%M")
    clock_label.configure(text=now)
    app.after(1000, update_clock)  # Update every second



# === Initial Setup Calls ===
apply_theme(current_theme_dict)  # Apply the loaded theme initially
update_clock()  # Start the clock


# === Start App ===
app.mainloop()
