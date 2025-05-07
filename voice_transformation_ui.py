import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import threading
import time
from voice_transformation import process_audio

class VoiceTransformationUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Transformation Tool")
        self.root.geometry("500x350")
        self.root.resizable(True, True)
        
        self.input_file = ""
        self.output_file = ""
        self.effect_type = tk.StringVar(value="radio")
        self.is_processing = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame for file selection
        file_frame = ttk.LabelFrame(self.root, text="File Selection")
        file_frame.pack(fill="x", expand="yes", padx=10, pady=10)
        
        # Input file
        ttk.Label(file_frame, text="Input Audio File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.input_entry = ttk.Entry(file_frame, width=40)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.select_input_file).grid(row=0, column=2, padx=5, pady=5)
        
        # Output file
        ttk.Label(file_frame, text="Output Audio File:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.output_entry = ttk.Entry(file_frame, width=40)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.select_output_file).grid(row=1, column=2, padx=5, pady=5)
        
        # Effect selection
        effect_frame = ttk.LabelFrame(self.root, text="Effect Selection")
        effect_frame.pack(fill="x", expand="yes", padx=10, pady=10)
        
        ttk.Radiobutton(effect_frame, text="Old Radio Effect", variable=self.effect_type, value="radio").pack(anchor="w", padx=5, pady=5)
        ttk.Radiobutton(effect_frame, text="Walkie-Talkie Effect", variable=self.effect_type, value="walkie").pack(anchor="w", padx=5, pady=5)
        
        # Process button
        process_frame = ttk.Frame(self.root)
        process_frame.pack(fill="x", expand="yes", padx=10, pady=10)
        
        self.process_button = ttk.Button(process_frame, text="Transform Voice", command=self.start_processing)
        self.process_button.pack(pady=10)
        
        # Progress indicator
        self.progress_bar = ttk.Progressbar(process_frame, orient="horizontal", length=300, mode="indeterminate")
        self.progress_bar.pack(pady=10, fill="x")
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(process_frame, textvariable=self.status_var).pack(pady=5)
    
    def select_input_file(self):
        filetypes = (
            ("Audio files", "*.wav *.mp3 *.ogg *.flac"),
            ("All files", "*.*")
        )
        filename = filedialog.askopenfilename(title="Select Audio File", filetypes=filetypes)
        if filename:
            self.input_file = filename
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)
            
            # Auto-generate output filename
            if not self.output_entry.get():
                base_name = os.path.splitext(os.path.basename(filename))[0]
                effect = self.effect_type.get()
                output_name = f"{base_name}_{effect}.wav"
                output_path = os.path.join(os.path.dirname(filename), output_name)
                self.output_file = output_path
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, output_path)
    
    def select_output_file(self):
        filetypes = (
            ("WAV files", "*.wav"),
            ("All files", "*.*")
        )
        filename = filedialog.asksaveasfilename(title="Save Output File", filetypes=filetypes, defaultextension=".wav")
        if filename:
            self.output_file = filename
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)
    
    def start_processing(self):
        # Validate inputs
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        effect = self.effect_type.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input audio file")
            return
        
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist")
            return
        
        # Start processing in a separate thread
        self.is_processing = True
        self.process_button.config(state="disabled")
        self.progress_bar.start(10)
        self.status_var.set("Processing...")
        
        processing_thread = threading.Thread(target=self.process_audio_file, args=(input_file, output_file, effect))
        processing_thread.daemon = True
        processing_thread.start()
    
    def process_audio_file(self, input_file, output_file, effect):
        try:
            process_audio(input_file, output_file, effect)
            self.root.after(0, self.processing_complete, True, "Processing complete!")
        except Exception as e:
            self.root.after(0, self.processing_complete, False, f"Error: {str(e)}")
    
    def processing_complete(self, success, message):
        self.progress_bar.stop()
        self.is_processing = False
        self.process_button.config(state="normal")
        self.status_var.set(message)
        
        if success:
            messagebox.showinfo("Success", f"Voice transformation complete!\nSaved to: {self.output_entry.get()}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceTransformationUI(root)
    root.mainloop() 