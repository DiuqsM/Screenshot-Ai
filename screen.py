import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab, ImageTk
import io
import base64
import google.generativeai as genai
import json
from datetime import datetime
import os

class ScreenshotAnalysisApp:
    def __init__(self):
        # Initialize main window but keep it hidden
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
        # Configure Gemini API (you'll need to add your API key)
        self.api_key = "AIzaSyByo297O1YjIm6MtwAwY5kYzBUppjqr2Q4"
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create screenshot button window
        self.button_window = tk.Toplevel()
        self.button_window.title("Screenshot Tool")
        self.button_window.geometry("200x50")
        
        # Create capture button
        self.capture_btn = ttk.Button(
            self.button_window,
            text="Capture Screenshot",
            command=self.capture_screenshot
        )
        self.capture_btn.pack(pady=10)
        
        # Initialize chat window (will be created after screenshot)
        self.chat_window = None
        self.screenshot_image = None
        self.messages = []

    def capture_screenshot(self):
        # Minimize windows temporarily
        self.button_window.iconify()
        
        # Wait a bit for windows to minimize
        self.root.after(500, self._take_screenshot)

    def _take_screenshot(self):
        # Capture the screen
        screenshot = ImageGrab.grab()
        self.screenshot_image = screenshot
        
        # Convert to base64 for Gemini API
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        self.screenshot_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Show chat window
        self.create_chat_window()
        
        # Restore button window
        self.button_window.deiconify()
        
        # Initial analysis
        self.analyze_with_gemini("What do you see in this screenshot? Please provide a brief analysis.")

    def create_chat_window(self):
        if self.chat_window:
            self.chat_window.destroy()
            
        self.chat_window = tk.Toplevel()
        self.chat_window.title("Screenshot Analysis")
        self.chat_window.geometry("600x800")
        
        # Create screenshot preview
        preview = ImageTk.PhotoImage(self.screenshot_image.resize((500, 300)))
        preview_label = ttk.Label(self.chat_window, image=preview)
        preview_label.image = preview  # Keep a reference
        preview_label.pack(pady=10)
        
        # Create chat area
        self.chat_area = tk.Text(self.chat_window, height=15, width=60, wrap=tk.WORD)
        self.chat_area.pack(pady=10, padx=10)
        self.chat_area.config(state=tk.DISABLED)
        
        # Create input area
        self.input_frame = ttk.Frame(self.chat_window)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.input_field = ttk.Entry(self.input_frame)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        send_btn = ttk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message
        )
        send_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to send message
        self.input_field.bind("<Return>", lambda e: self.send_message())

    def send_message(self):
        message = self.input_field.get().strip()
        if message:
            self.input_field.delete(0, tk.END)
            self.analyze_with_gemini(message)

    def analyze_with_gemini(self, message):
        # Add user message to chat
        self.add_message("User", message)
        
        try:
            # Convert PIL Image to bytes for Gemini
            image_bytes = io.BytesIO()
            self.screenshot_image.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            
            # Get response from Gemini
            response = self.model.generate_content([
                message,
                {"mime_type": "image/png", "data": image_bytes}
            ])
            
            # Add response to chat
            self.add_message("Assistant", response.text)
            
        except Exception as e:
            self.add_message("System", f"Error: {str(e)}")

    def add_message(self, sender, message):
        self.messages.append({"sender": sender, "message": message})
        
        # Update chat area
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"\n{sender}: {message}\n")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenshotAnalysisApp()
    app.run()
