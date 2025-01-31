import tkinter as tk
from tkinter import ttk, font
from PIL import ImageGrab, ImageTk
import io
import base64
import google.generativeai as genai
from datetime import datetime
import os
import tempfile
from tkinter import Scrollbar

class ScreenshotAnalysisApp:
    def __init__(self):
        # Initialize main window but keep it hidden
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Set up custom fonts
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=11, family="Helvetica")
        
        # Create temporary directory for screenshots
        self.temp_dir = tempfile.gettempdir()
        self.screenshots_dir = os.path.join(self.temp_dir, 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Configure Gemini API
        self.api_key = "AIzaSyByo297O1YjIm6MtwAwY5kYzBUppjqr2Q4"
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create screenshot button window
        self.button_window = tk.Toplevel()
        self.button_window.title("Screenshot Tool")
        self.button_window.geometry("200x50")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("Modern.TButton", 
                           padding=10, 
                           font=("Helvetica", 11))
        
        # Create capture button
        self.capture_btn = ttk.Button(
            self.button_window,
            text="Capture Screenshot",
            command=self.capture_screenshot,
            style="Modern.TButton"
        )
        self.capture_btn.pack(pady=10)
        
        self.chat_window = None
        self.screenshot_image = None
        self.current_screenshot_path = None
        self.messages = []

    def capture_screenshot(self):
        self.button_window.iconify()
        self.root.after(500, self._take_screenshot)

    def _take_screenshot(self):
        screenshot = ImageGrab.grab()
        self.screenshot_image = screenshot
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        self.current_screenshot_path = os.path.join(self.screenshots_dir, filename)
        screenshot.save(self.current_screenshot_path)
        
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        self.screenshot_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        self.create_chat_window()
        self.button_window.deiconify()
        
        # Add welcome message
        self.add_message("Assistant", "Hello, how can I help you analyze this screenshot?")

    def create_chat_window(self):
        if self.chat_window:
            self.chat_window.destroy()
            
        self.chat_window = tk.Toplevel()
        self.chat_window.title("Screenshot Analysis")
        self.chat_window.geometry("800x900")
        
        # Configure weights for responsive layout
        self.chat_window.grid_rowconfigure(2, weight=1)
        self.chat_window.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = ttk.Frame(self.chat_window)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Preview frame with modern styling
        preview_frame = ttk.Frame(main_container)
        preview_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Resize screenshot for preview
        width = 700
        height = int((width/self.screenshot_image.width) * self.screenshot_image.height)
        preview = ImageTk.PhotoImage(self.screenshot_image.resize((width, height)))
        preview_label = ttk.Label(preview_frame, image=preview)
        preview_label.image = preview
        preview_label.pack()
        
        # Chat container with custom styling
        chat_container = ttk.Frame(main_container)
        chat_container.grid(row=1, column=0, sticky="nsew")
        chat_container.grid_rowconfigure(0, weight=1)
        chat_container.grid_columnconfigure(0, weight=1)
        
        # Create chat area with scrollbar
        chat_frame = ttk.Frame(chat_container)
        chat_frame.grid(row=0, column=0, sticky="nsew")
        
        self.chat_area = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            bg="#ffffff",
            height=15
        )
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_area.yview)
        self.chat_area.configure(yscrollcommand=scrollbar.set)
        
        self.chat_area.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        
        # Input container with dynamic width
        input_container = ttk.Frame(main_container)
        input_container.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        input_container.grid_columnconfigure(0, weight=1)
        
        # Modern input field
        self.input_field = ttk.Entry(
            input_container,
            font=("Helvetica", 12),
            style="Modern.TEntry"
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Modern send button
        send_btn = ttk.Button(
            input_container,
            text="Send",
            command=self.send_message,
            style="Modern.TButton"
        )
        send_btn.grid(row=0, column=1)
        
        # Configure chat area
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.tag_configure("user", foreground="#0056b3", font=("Helvetica", 12, "bold"))
        self.chat_area.tag_configure("assistant", foreground="#2e7d32", font=("Helvetica", 12))
        
        # Bind Enter key
        self.input_field.bind("<Return>", lambda e: self.send_message())
        
        # Set focus to input field
        self.input_field.focus_set()

    def send_message(self):
        message = self.input_field.get().strip()
        if message:
            self.input_field.delete(0, tk.END)
            self.analyze_with_gemini(message)

    def analyze_with_gemini(self, message):
        self.add_message("User", message, "user")
        
        try:
            image_bytes = io.BytesIO()
            self.screenshot_image.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            
            response = self.model.generate_content([
                message,
                {"mime_type": "image/png", "data": image_bytes}
            ])
            
            self.add_message("Assistant", response.text, "assistant")
            
        except Exception as e:
            self.add_message("System", f"Error: {str(e)}", "assistant")

    def add_message(self, sender, message, tag=None):
        self.messages.append({"sender": sender, "message": message})
        
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"\n{sender}: ", tag)
        self.chat_area.insert(tk.END, f"{message}\n", tag)
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenshotAnalysisApp()
    app.run()
