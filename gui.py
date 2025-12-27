import os
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import scrolledtext
import threading

from calculator import core
from calculator import renamer


class VideoDurationCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Duration Calculator")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f3ff")

        self.video_extensions = ['.mp4', '.m4v', '.avi', '.mov', '.mkv',
                                '.flv', '.wmv', '.webm', '.ts']

        self.is_processing = False
        self.cancel_processing = False
        self.selected_folder = tk.StringVar()
        self.extensions_var = tk.StringVar(value=', '.join(self.video_extensions))
        self.folder_summaries = []  
        self.rename_history = []  

        self.is_dark_mode = False
        self.themes = {
            'dark': {
                'bg': '#1a1a2e',
                'header_bg': '#16213e',
                'input_bg': '#0f3460',
                'text': '#ffffff',
                'accent': '#e94560',
                'secondary': '#533483',
                'tertiary': '#00d4ff',
                'muted': '#aaaaaa'
            },
            'light': {
                'bg': '#f5f3ff',
                'header_bg': '#ffffff',
                'input_bg': '#faf8ff',
                'text': '#2d1b69',
                'accent': '#7c3aed',
                'secondary': '#a855f7',
                'tertiary': '#6366f1',
                'muted': '#6b7280'
            }
        }

        self.setup_ui()

    def setup_ui(self):
        theme = self.themes['dark' if self.is_dark_mode else 'light']

        header_frame = tk.Frame(self.root, bg=theme['header_bg'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)

        title_container = tk.Frame(header_frame, bg=theme['header_bg'])
        title_container.pack(expand=True, fill=tk.BOTH)

        title_label = tk.Label(title_container, text="🎬 Video Duration Calculator",
                              font=("Helvetica", 24, "bold"),
                              bg=theme['header_bg'], fg=theme['accent'])
        title_label.pack(side=tk.LEFT, padx=10, pady=20)

        self.theme_btn = tk.Button(title_container, text="☀" if self.is_dark_mode else "🌙",
                                   command=self.toggle_theme,
                                   font=("Helvetica", 16),
                                   bg=theme['secondary'], fg="white",
                                   activebackground=theme['accent'],
                                   cursor="hand2", padx=15, pady=5,
                                   relief=tk.FLAT)
        self.theme_btn.pack(side=tk.RIGHT, padx=10)

        folder_frame = tk.Frame(self.root, bg=theme['header_bg'])
        folder_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(folder_frame, text="Selected Folder:",
                font=("Helvetica", 11), bg=theme['header_bg'], fg=theme['text']).pack(anchor=tk.W, padx=10, pady=(10, 5))

        self.path_display = tk.Entry(folder_frame, textvariable=self.selected_folder,
                               font=("Helvetica", 10), state="readonly",
                               bg=theme['input_bg'], fg=theme['text'],
                               readonlybackground=theme['input_bg'])
        self.path_display.pack(fill=tk.X, padx=10, pady=(0, 10))

        extensions_frame = tk.Frame(self.root, bg=theme['header_bg'])
        extensions_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(extensions_frame, text="Video File Extensions:",
                font=("Helvetica", 11), bg=theme['header_bg'], fg=theme['text']).pack(anchor=tk.W, padx=10, pady=(10, 5))

        extensions_entry_frame = tk.Frame(extensions_frame, bg=theme['header_bg'])
        extensions_entry_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.extensions_entry = tk.Entry(extensions_entry_frame,
                                         textvariable=self.extensions_var,
                                         font=("Helvetica", 10),
                                         bg=theme['input_bg'], fg=theme['text'],
                                         insertbackground=theme['text'])
        self.extensions_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.update_ext_btn = tk.Button(extensions_entry_frame, text="Update",
                                   command=self.update_extensions,
                                   font=("Helvetica", 9, "bold"),
                                   bg=theme['tertiary'], fg="white",
                                   activebackground=theme['secondary'],
                                   cursor="hand2", padx=15, pady=5,
                                   relief=tk.FLAT)
        self.update_ext_btn.pack(side=tk.LEFT)

        tk.Label(extensions_frame,
                text="Separate extensions with commas (e.g., .mp4, .avi, .mkv)",
                font=("Helvetica", 9, "italic"),
                bg=theme['header_bg'], fg=theme['muted']).pack(anchor=tk.W, padx=10, pady=(0, 10))

        button_frame = tk.Frame(self.root, bg=theme['bg'])
        button_frame.pack(pady=10)

        self.select_btn = tk.Button(button_frame, text="📁 Select Folder",
                                    command=self.select_folder,
                                    font=("Helvetica", 12, "bold"),
                                    bg=theme['accent'], fg="white",
                                    activebackground=theme['secondary'],
                                    cursor="hand2", padx=20, pady=10,
                                    relief=tk.FLAT)
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.process_btn = tk.Button(button_frame, text="▶ Calculate Duration",
                                     command=self.start_processing,
                                     font=("Helvetica", 12, "bold"),
                                     bg=theme['secondary'], fg="white",
                                     activebackground=theme['accent'],
                                     cursor="hand2", padx=20, pady=10,
                                     relief=tk.FLAT, state=tk.DISABLED)
        self.process_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = tk.Button(button_frame, text="⏹ Cancel",
                                    command=self.cancel_processing_task,
                                    font=("Helvetica", 12, "bold"),
                                    bg="#dc2626", fg="white",
                                    activebackground="#991b1b",
                                    cursor="hand2", padx=20, pady=10,
                                    relief=tk.FLAT, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        self.rename_btn = tk.Button(button_frame, text="📝 Rename Folders",
                                    command=self.rename_folders_with_duration,
                                    font=("Helvetica", 12, "bold"),
                                    bg="#059669", fg="white",
                                    activebackground="#047857",
                                    cursor="hand2", padx=20, pady=10,
                                    relief=tk.FLAT, state=tk.DISABLED)
        self.rename_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_rename_btn = tk.Button(button_frame, text="↶ Cancel Rename",
                                           command=self.revert_renames,
                                           font=("Helvetica", 12, "bold"),
                                           bg="#b45309", fg="white",
                                           activebackground="#92400e",
                                           cursor="hand2", padx=15, pady=10,
                                           relief=tk.FLAT, state=tk.DISABLED)
        self.cancel_rename_btn.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(self.root, mode='indeterminate', length=860)
        self.progress.pack(padx=20, pady=10)

        self.status_label = tk.Label(self.root, text="Select a folder to begin",
                                     font=("Helvetica", 10, "italic"),
                                     bg=theme['bg'], fg=theme['muted'])
        self.status_label.pack(pady=5)

        results_frame = tk.Frame(self.root, bg=theme['header_bg'])
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(results_frame, text="Results:",
                font=("Helvetica", 12, "bold"),
                bg=theme['header_bg'], fg=theme['text']).pack(anchor=tk.W, padx=10, pady=(10, 5))

        self.results_text = scrolledtext.ScrolledText(results_frame,
                                                      font=("Courier", 10),
                                                      bg=theme['input_bg'], fg=theme['text'],
                                                      insertbackground=theme['text'],
                                                      relief=tk.FLAT,
                                                      wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.update_text_tags()

    def update_text_tags(self):
        """Update text tags colors based on theme"""
        if self.is_dark_mode:
            self.results_text.tag_configure("header", foreground="#e94560", font=("Courier", 10, "bold"))
            self.results_text.tag_configure("folder", foreground="#00d4ff", font=("Courier", 10, "bold"))
            self.results_text.tag_configure("total", foreground="#50fa7b", font=("Courier", 11, "bold"))
            self.results_text.tag_configure("grand", foreground="#ff6ac1", font=("Courier", 12, "bold"))
        else:
            self.results_text.tag_configure("header", foreground="#7c3aed", font=("Courier", 10, "bold"))
            self.results_text.tag_configure("folder", foreground="#6366f1", font=("Courier", 10, "bold"))
            self.results_text.tag_configure("total", foreground="#059669", font=("Courier", 11, "bold"))
            self.results_text.tag_configure("grand", foreground="#a855f7", font=("Courier", 12, "bold"))

    def toggle_theme(self):
        """Toggle between dark and light mode"""
        self.is_dark_mode = not self.is_dark_mode
        theme = self.themes['dark' if self.is_dark_mode else 'light']

        self.root.configure(bg=theme['bg'])
        self.theme_btn.config(text="☀" if self.is_dark_mode else "🌙",
                             bg=theme['secondary'])

        for widget in self.root.winfo_children():
            self.update_widget_theme(widget, theme)

        self.update_text_tags()

    def update_widget_theme(self, widget, theme):
        """Recursively update widget colors"""
        widget_type = widget.winfo_class()

        if widget_type == 'Frame':
            if widget.cget('bg') in ['#1a1a2e', '#f5f3ff']:
                widget.config(bg=theme['bg'])
            elif widget.cget('bg') in ['#16213e', '#ffffff']:
                widget.config(bg=theme['header_bg'])
        elif widget_type == 'Label':
            widget.config(bg=widget.master.cget('bg'))
            if 'foreground' in widget.keys():
                current_fg = widget.cget('fg')
                if current_fg in ['#e94560', '#7c3aed']:
                    widget.config(fg=theme['accent'])
                elif current_fg in ['#ffffff', '#2d1b69']:
                    widget.config(fg=theme['text'])
                elif current_fg in ['#aaaaaa', '#888888', '#6b7280']:
                    widget.config(fg=theme['muted'])
        elif widget_type == 'Button':
            if widget == self.select_btn:
                widget.config(bg=theme['accent'], activebackground=theme['secondary'])
            elif widget == self.process_btn:
                widget.config(bg=theme['secondary'], activebackground=theme['accent'])
            elif widget == self.update_ext_btn:
                widget.config(bg=theme['tertiary'], activebackground=theme['secondary'])
            elif widget == self.cancel_btn:
                widget.config(bg="#dc2626", activebackground="#991b1b")
            elif widget == self.rename_btn:
                widget.config(bg="#059669", activebackground="#047857")
            elif widget == getattr(self, 'cancel_rename_btn', None):
                widget.config(bg="#b45309", activebackground="#92400e")
        elif widget_type == 'Entry':
            widget.config(bg=theme['input_bg'], fg=theme['text'],
                         insertbackground=theme['text'])
            if 'readonlybackground' in widget.keys():
                widget.config(readonlybackground=theme['input_bg'])
        elif widget_type == 'Text':
            widget.config(bg=theme['input_bg'], fg=theme['text'],
                         insertbackground=theme['text'])

        for child in widget.winfo_children():
            self.update_widget_theme(child, theme)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Videos")
        if folder:
            self.selected_folder.set(folder)
            self.process_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"Ready to process: {os.path.basename(folder)}")
            self.results_text.delete(1.0, tk.END)

    def update_extensions(self):
        """Update the video extensions list from user input"""
        try:
            extensions_text = self.extensions_var.get()
            extensions_list = [ext.strip() for ext in extensions_text.split(',')]

            validated_extensions = []
            for ext in extensions_list:
                ext = ext.strip()
                if ext:
                    if not ext.startswith('.'):
                        ext = '.' + ext
                    validated_extensions.append(ext.lower())

            if validated_extensions:
                self.video_extensions = validated_extensions
                self.extensions_var.set(', '.join(self.video_extensions))
                self.status_label.config(text=f"✓ Extensions updated: {len(self.video_extensions)} formats")
                self.log_result(f"\n✓ Video extensions updated: {', '.join(self.video_extensions)}\n\n", "total")
            else:
                self.status_label.config(text="⚠ Please enter at least one extension")
        except Exception as e:
            self.status_label.config(text=f"⚠ Error updating extensions: {str(e)}")

    def start_processing(self):
        if not self.selected_folder.get():
            return

        self.is_processing = True
        self.cancel_processing = False
        self.folder_summaries.clear()
        self.select_btn.config(state=tk.DISABLED)
        self.process_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress.start(10)
        self.status_label.config(text="Processing videos...")
        self.results_text.delete(1.0, tk.END)

        thread = threading.Thread(target=self.process_videos, daemon=True)
        thread.start()

    def cancel_processing_task(self):
        self.cancel_processing = True
        self.status_label.config(text="Cancelling...")
        self.log_result("\n\n⚠ PROCESSING CANCELLED BY USER\n", "header")

    def process_videos(self):
        try:
            folder_summaries, grand_total, total_videos = core.traverse_and_calculate(
                self.selected_folder.get(),
                self.video_extensions,
                cancel_check=lambda: self.cancel_processing,
                logger=self.log_result
            )
            self.folder_summaries = folder_summaries
        except Exception as e:
            if not self.cancel_processing:
                self.log_result(f"\n❌ Error: {str(e)}\n", "header")
        finally:
            self.root.after(0, self.processing_complete)

    def processing_complete(self):
        self.is_processing = False
        self.cancel_processing = False
        self.progress.stop()
        self.select_btn.config(state=tk.NORMAL)
        self.process_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)

        if self.cancel_processing:
            self.status_label.config(text="Processing cancelled")
        else:
            self.status_label.config(text="Processing complete!")
            if self.folder_summaries:
                self.rename_btn.config(state=tk.NORMAL)

    def log_result(self, text, tag=None):
        def update():
            self.results_text.insert(tk.END, text, tag)
            self.results_text.see(tk.END)
            self.results_text.update_idletasks()

        self.root.after(0, update)

    def rename_folders_with_duration(self):
        if not self.folder_summaries:
            self.status_label.config(text="No folders to rename")
            return

        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Confirm Rename",
            f"This will rename {len(self.folder_summaries)} folders by adding duration.\n\n"
            "Example:\n"
            "  '01. Introduction' → '01. Introduction (33 min)'\n\n"
            "Continue?"
        )

        if not confirm:
            return

        rename_history, summary = renamer.rename_folders_with_duration(self.folder_summaries, logger=self.log_result)
        self.rename_history = rename_history

        self.status_label.config(text=f"Renamed {summary.get('renamed', 0)} folders")

        if summary.get('renamed', 0) > 0:
            self.rename_btn.config(state=tk.DISABLED)
            self.cancel_rename_btn.config(state=tk.NORMAL)

    def revert_renames(self):
        if not self.rename_history:
            self.status_label.config(text="No rename operations to revert")
            return

        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Confirm Revert",
            f"This will attempt to revert {len(self.rename_history)} renames and restore original folder names. Continue?"
        )
        if not confirm:
            return

        result = renamer.revert_renames(self.rename_history, logger=self.log_result)
        self.status_label.config(text=f"Reverted {result.get('reverted', 0)} renames")

        if result.get('reverted', 0) > 0:
            self.rename_btn.config(state=tk.NORMAL)
        self.cancel_rename_btn.config(state=tk.DISABLED)
        self.rename_history = []

