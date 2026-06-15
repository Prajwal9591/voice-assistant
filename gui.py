import customtkinter as ctk
import tkinter as tk
import math
import logging
import queue
import sys

logger = logging.getLogger("Jarvis.GUI")

# Set customtkinter appearance guidelines
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JarvisGUI:
    def __init__(self, root, on_command_submit=None, on_voice_toggle=None, on_settings_change=None):
        """
        Initializes the modern customtkinter Jarvis dashboard.
        
        :param root: The ctk.CTk window root object
        :param on_command_submit: Callback when user sends manual text command (func(text))
        :param on_voice_toggle: Callback when speech recognition is toggled (func(is_enabled))
        :param on_settings_change: Callback when vocal settings change (func(key, val))
        """
        self.root = root
        self.on_command_submit = on_command_submit
        self.on_voice_toggle = on_voice_toggle
        self.on_settings_change = on_settings_change
        
        # Thread safety queue
        self.gui_queue = queue.Queue()
        
        # Futuristic Cyber Colors
        self.color_obsidian = "#080B10"   # Background space black
        self.color_card = "#111622"       # Deep frame cards
        self.color_cyan = "#00F0FF"       # Jarvis electric cyan (Idle/Speech)
        self.color_amber = "#FF7B00"      # Mic listening orange
        self.color_purple = "#BD00FF"     # AI thinking violet
        self.color_green = "#00FF66"      # Normal online green
        self.color_crimson = "#FF3B30"    # Stop button red
        
        # Configure Root Window Properties
        self.root.title("J.A.R.V.I.S. - COGNITIVE OPERATING BOARD")
        self.root.geometry("1100x750")
        self.root.configure(fg_color=self.color_obsidian)
        
        # Grid Configurations for 100% responsiveness
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # App State Indicators
        self.voice_active = tk.BooleanVar(value=True)
        self.current_state = "idle"  # idle, listening, thinking, speaking
        self.reactor_angle = 0.0
        self.pulse_phase = 0.0
        
        # Build UI layout
        self._create_layout()
        
        # Start core HUD animations
        self._animate_hud()
        
        # Start queue safety loop
        self._check_queue()
        
        # Launch professional sci-fi loading boot animation
        self._show_boot_animation()
        
        # Bind close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_layout(self):
        # 1. Main Responsive Master Frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.color_obsidian, corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # Define 2 column layout: Left (HUD & Controls), Right (Dialogue & Logs)
        self.main_frame.grid_columnconfigure(0, weight=9)  # Left panel gets 45%
        self.main_frame.grid_columnconfigure(1, weight=11) # Right panel gets 55%
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # =========================================================================
        # LEFT COLUMN: HUD CORE & SETTINGS CONTROL
        # =========================================================================
        self.left_column = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.left_column.grid_rowconfigure(0, weight=12) # HUD gets most vertical space
        self.left_column.grid_rowconfigure(1, weight=8)  # Settings gets lower third
        self.left_column.grid_columnconfigure(0, weight=1)
        
        # --- HUD CORE CARD ---
        self.hud_card = ctk.CTkFrame(self.left_column, fg_color=self.color_card, corner_radius=15, border_width=1, border_color="#1E293B")
        self.hud_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Title
        self.lbl_hud_title = ctk.CTkLabel(
            self.hud_card, 
            text="// COGNITIVE CORE RENDERER", 
            font=("Consolas", 13, "bold"), 
            text_color=self.color_cyan
        )
        self.lbl_hud_title.pack(anchor="w", padx=20, pady=(20, 5))
        
        # Status Light Bar
        self.lbl_status_bar = ctk.CTkLabel(
            self.hud_card, 
            text="SYSTEM READY // IDLE", 
            font=("Consolas", 10, "bold"), 
            text_color=self.color_green
        )
        self.lbl_status_bar.pack(anchor="w", padx=20, pady=(0, 10))
        
        # HUD Core Visualizer Container (Relative Layout for Arc Reactor + Floating Button overlay)
        self.hud_container = ctk.CTkFrame(self.hud_card, fg_color="transparent")
        self.hud_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Interactive Animated HUD Canvas
        self.canvas = ctk.CTkCanvas(self.hud_container, width=280, height=280, bg=self.color_card, highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")
        
        # Floating CIRCULAR MICROPHONE BUTTON exactly in the center of canvas reactor rings
        self.btn_mic = ctk.CTkButton(
            self.hud_container,
            text="🎙️",
            width=90,
            height=90,
            corner_radius=45,
            fg_color="#172230",
            hover_color=self.color_cyan,
            border_color=self.color_cyan,
            border_width=2,
            font=("Segoe UI", 34),
            text_color=self.color_cyan,
            command=self._on_mic_button_clicked
        )
        self.btn_mic.place(relx=0.5, rely=0.5, anchor="center")
        
        # Start Listening / Stop Listening Button Row (CTA buttons)
        self.hud_btn_row = ctk.CTkFrame(self.hud_card, fg_color="transparent")
        self.hud_btn_row.pack(fill=tk.X, padx=20, pady=(0, 20))
        self.hud_btn_row.grid_columnconfigure(0, weight=1)
        self.hud_btn_row.grid_columnconfigure(1, weight=1)
        
        self.btn_start = ctk.CTkButton(
            self.hud_btn_row,
            text="START LISTENING",
            fg_color="#006644",
            hover_color=self.color_green,
            text_color="#FFF",
            font=("Segoe UI", 11, "bold"),
            height=38,
            corner_radius=8,
            command=self._start_listening
        )
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_stop = ctk.CTkButton(
            self.hud_btn_row,
            text="STOP CORE",
            fg_color="#5E1616",
            hover_color=self.color_crimson,
            text_color="#FFF",
            font=("Segoe UI", 11, "bold"),
            height=38,
            corner_radius=8,
            command=self._stop_listening
        )
        self.btn_stop.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # --- VOCAL SETTINGS CARD ---
        self.settings_card = ctk.CTkFrame(self.left_column, fg_color=self.color_card, corner_radius=15, border_width=1, border_color="#1E293B")
        self.settings_card.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        self.lbl_settings_title = ctk.CTkLabel(
            self.settings_card, 
            text="// VOCAL SYSTEM CONFIGURATIONS", 
            font=("Consolas", 13, "bold"), 
            text_color=self.color_cyan
        )
        self.lbl_settings_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Speed Rate Slider Panel
        self.settings_grid = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.settings_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        self.settings_grid.grid_columnconfigure(0, weight=1)
        self.settings_grid.grid_columnconfigure(1, weight=1)
        
        # Volume slider
        self.vol_lbl = ctk.CTkLabel(self.settings_grid, text="TTS VOLUME", font=("Consolas", 9), text_color="#94A3B8")
        self.vol_lbl.grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.slider_volume = ctk.CTkSlider(self.settings_grid, from_=0.0, to=1.0, number_of_steps=100, command=self._on_volume_slider)
        self.slider_volume.set(1.0)
        self.slider_volume.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        
        # Rate Slider
        self.rate_lbl = ctk.CTkLabel(self.settings_grid, text="SPEECH SPEED", font=("Consolas", 9), text_color="#94A3B8")
        self.rate_lbl.grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.slider_rate = ctk.CTkSlider(self.settings_grid, from_=100, to=300, number_of_steps=200, command=self._on_rate_slider)
        self.slider_rate.set(175)
        self.slider_rate.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        # Gender Selection dropdown
        self.gender_lbl = ctk.CTkLabel(self.settings_grid, text="VOICE SYNTHESIS MODEL", font=("Consolas", 9), text_color="#94A3B8")
        self.gender_lbl.grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.gender_combo = ctk.CTkComboBox(
            self.settings_grid, 
            values=["Female", "Male"], 
            state="readonly", 
            corner_radius=6, 
            height=28,
            command=self._on_voice_changed
        )
        self.gender_combo.set("Female")
        self.gender_combo.grid(row=3, column=0, sticky="ew", padx=(0, 10))
        
        # Mode display
        self.mode_lbl = ctk.CTkLabel(self.settings_grid, text="LISTENER STATUS", font=("Consolas", 9), text_color="#94A3B8")
        self.mode_lbl.grid(row=2, column=1, sticky="w", pady=(0, 2))
        self.lbl_mic_status_badge = ctk.CTkLabel(
            self.settings_grid, 
            text="CONTINUOUS DUPLEX", 
            font=("Consolas", 10, "bold"), 
            text_color=self.color_cyan,
            fg_color="#172F3E",
            corner_radius=4,
            height=28
        )
        self.lbl_mic_status_badge.grid(row=3, column=1, sticky="ew", padx=(10, 0))
        
        # =========================================================================
        # RIGHT COLUMN: DIALOGUE DISPLAY & TECHNICAL DIAGNOSTICS
        # =========================================================================
        self.right_column = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.right_column.grid_rowconfigure(0, weight=13) # Dialogue frame
        self.right_column.grid_rowconfigure(1, weight=7)  # Diagnostics frame
        self.right_column.grid_columnconfigure(0, weight=1)
        
        # --- CONVERSATION DIALOGUE CARD ---
        self.dialogue_card = ctk.CTkFrame(self.right_column, fg_color=self.color_card, corner_radius=15, border_width=1, border_color="#1E293B")
        self.dialogue_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        self.lbl_dialogue_title = ctk.CTkLabel(
            self.dialogue_card, 
            text="// CONVERSATIONAL DATA COCKPIT", 
            font=("Consolas", 13, "bold"), 
            text_color=self.color_cyan
        )
        self.lbl_dialogue_title.pack(anchor="w", padx=20, pady=(20, 5))
        
        # REAL-TIME COMMAND DISPLAY & VOICE RESPONSE DISPLAY CARDS (Requirement satisfaction)
        self.split_display_row = ctk.CTkFrame(self.dialogue_card, fg_color="transparent")
        self.split_display_row.pack(fill=tk.X, padx=20, pady=5)
        self.split_display_row.grid_columnconfigure(0, weight=1)
        self.split_display_row.grid_columnconfigure(1, weight=1)
        
        # Real-time Command Card
        self.cmd_card = ctk.CTkFrame(self.split_display_row, fg_color="#172230", border_width=1, border_color="#2A384F", corner_radius=8)
        self.cmd_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=2)
        ctk.CTkLabel(self.cmd_card, text="REAL-TIME SPEECH INPUT", font=("Consolas", 8, "bold"), text_color=self.color_amber).pack(anchor="w", padx=10, pady=(6, 0))
        self.lbl_realtime_cmd = ctk.CTkLabel(self.cmd_card, text="Waiting for command...", font=("Segoe UI", 10, "italic"), text_color="#94A3B8", wraplength=220, justify="left")
        self.lbl_realtime_cmd.pack(anchor="w", padx=10, pady=(2, 8))
        
        # Voice Response Card
        self.res_card = ctk.CTkFrame(self.split_display_row, fg_color="#122B29", border_width=1, border_color="#1F4743", corner_radius=8)
        self.res_card.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=2)
        ctk.CTkLabel(self.res_card, text="ASSISTANT AUDIO OUTPUT", font=("Consolas", 8, "bold"), text_color=self.color_cyan).pack(anchor="w", padx=10, pady=(6, 0))
        self.lbl_realtime_res = ctk.CTkLabel(self.res_card, text="Ready to speak, sir.", font=("Segoe UI", 10, "italic"), text_color="#94A3B8", wraplength=220, justify="left")
        self.lbl_realtime_res.pack(anchor="w", padx=10, pady=(2, 8))
        
        # Main dialog dialogue box (scrolling history)
        self.txt_dialog = ctk.CTkTextbox(
            self.dialogue_card,
            fg_color=self.color_obsidian,
            text_color="#ECEFF1",
            font=("Consolas", 10),
            border_width=1,
            border_color="#1E293B",
            corner_radius=10
        )
        self.txt_dialog.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.txt_dialog.configure(state="disabled")
        
        # Manual overrides entry frame
        self.override_frame = ctk.CTkFrame(self.dialogue_card, fg_color="transparent")
        self.override_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.ent_command = ctk.CTkEntry(
            self.override_frame,
            placeholder_text="Enter manual text override command...",
            fg_color=self.color_obsidian,
            text_color=self.color_cyan,
            placeholder_text_color="#475569",
            font=("Consolas", 11),
            border_color="#1E293B",
            height=38,
            corner_radius=8
        )
        self.ent_command.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.ent_command.bind("<Return>", lambda event: self._submit_manual_command())
        
        self.btn_send = ctk.CTkButton(
            self.override_frame,
            text="SUBMIT",
            fg_color="#1D2A44",
            hover_color=self.color_cyan,
            text_color=self.color_cyan,
            font=("Segoe UI", 11, "bold"),
            width=90,
            height=38,
            corner_radius=8,
            command=self._submit_manual_command
        )
        self.btn_send.pack(side=tk.RIGHT)
        
        # --- TECHNICAL LOGS CARD ---
        self.logs_card = ctk.CTkFrame(self.right_column, fg_color=self.color_card, corner_radius=15, border_width=1, border_color="#1E293B")
        self.logs_card.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        self.lbl_logs_title = ctk.CTkLabel(
            self.logs_card, 
            text="// DIAGNOSTICS & SYSTEM PIPELINES", 
            font=("Consolas", 13, "bold"), 
            text_color=self.color_cyan
        )
        self.lbl_logs_title.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.txt_logs = ctk.CTkTextbox(
            self.logs_card,
            fg_color=self.color_obsidian,
            text_color="#64748B",
            font=("Consolas", 8),
            border_width=1,
            border_color="#1E293B",
            corner_radius=10
        )
        self.txt_logs.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        self.txt_logs.configure(state="disabled")

    # =========================================================================
    # INTENT INTERACTION & TRIGGERS
    # =========================================================================
    
    def _on_mic_button_clicked(self):
        """Microphone core CTA button toggled. Suspends or runs voice activation."""
        active = not self.voice_active.get()
        self._set_voice_active_state(active)
        
    def _start_listening(self):
        """Dedicated Start button triggers speech listening loops."""
        self._set_voice_active_state(True)
        
    def _stop_listening(self):
        """Dedicated Stop button suspends listening and forces idle status."""
        self._set_voice_active_state(False)
        self.set_state("idle")

    def _set_voice_active_state(self, active: bool):
        self.voice_active.set(active)
        
        if active:
            # Change UI elements
            self.btn_mic.configure(
                fg_color="#1A2F25",
                text_color=self.color_cyan,
                border_color=self.color_cyan
            )
            self.lbl_mic_status_badge.configure(
                text="CONTINUOUS DUPLEX",
                text_color=self.color_cyan,
                fg_color="#172F3E"
            )
            self.append_log("[GUI]: Voice pipeline captures enabled.")
        else:
            # Dim UI elements
            self.btn_mic.configure(
                fg_color="#2A1B1C",
                text_color=self.color_crimson,
                border_color=self.color_crimson
            )
            self.lbl_mic_status_badge.configure(
                text="MANUAL OVERRIDE ONLY",
                text_color="#FF6B6B",
                fg_color="#3A1C1E"
            )
            self.append_log("[GUI]: Auditory continuous loop suspended. Text triggers only.")
            self.set_state("idle")
            
        if self.on_voice_toggle:
            self.on_voice_toggle(active)

    def _submit_manual_command(self):
        cmd = self.ent_command.get().strip()
        if not cmd:
            return
            
        self.ent_command.delete(0, tk.END)
        self.append_dialog(f"USER (Typed): {cmd}", is_user=True)
        self.append_log(f"[Manual Override Input]: Processing text command '{cmd}'")
        
        if self.on_command_submit:
            import threading
            threading.Thread(target=self.on_command_submit, args=(cmd,), daemon=True).start()

    def _on_rate_slider(self, val):
        rate = int(val)
        if self.on_settings_change:
            self.on_settings_change("rate", rate)

    def _on_volume_slider(self, val):
        vol = float(val)
        if self.on_settings_change:
            self.on_settings_change("volume", vol)

    def _on_voice_changed(self, gender):
        if self.on_settings_change:
            self.on_settings_change("voice", gender.lower())

    # =========================================================================
    # THREAD-SAFE QUEUE CONSOLE MANAGEMENT
    # =========================================================================
    
    def set_state(self, state):
        self.gui_queue.put(("state", state))

    def append_dialog(self, text, is_user=False):
        self.gui_queue.put(("dialog", (text, is_user)))

    def append_log(self, text):
        self.gui_queue.put(("log", text))

    def _check_queue(self):
        try:
            while True:
                task_type, payload = self.gui_queue.get_nowait()
                if task_type == "state":
                    self._update_state_ui(payload)
                elif task_type == "dialog":
                    text, is_user = payload
                    self._update_dialog_ui(text, is_user)
                elif task_type == "log":
                    self._update_log_ui(payload)
                self.gui_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(80, self._check_queue)

    def _update_state_ui(self, state):
        self.current_state = state.lower()
        
        # Color-coded theme changes
        if self.current_state == "idle":
            theme_color = self.color_cyan
            self.lbl_status_bar.configure(text="SYSTEM READY // ONLINE (IDLE)", text_color=self.color_green)
            self.btn_mic.configure(hover_color=self.color_cyan, text_color=self.color_cyan)
        elif self.current_state == "listening":
            theme_color = self.color_amber
            self.lbl_status_bar.configure(text="SYSTEM ACTIVE // CAPTURING AUDIO STREAM...", text_color=self.color_amber)
            self.btn_mic.configure(hover_color=self.color_amber, text_color=self.color_amber)
        elif self.current_state == "thinking":
            theme_color = self.color_purple
            self.lbl_status_bar.configure(text="NEURAL MATRIX ROUTING // PARSING TOKENS...", text_color=self.color_purple)
            self.btn_mic.configure(hover_color=self.color_purple, text_color=self.color_purple)
        elif self.current_state == "speaking":
            theme_color = self.color_cyan
            self.lbl_status_bar.configure(text="SYNTHESIZER CORE ACTIVE // GENERATING VOICE WAVE...", text_color=self.color_cyan)
            self.btn_mic.configure(hover_color=self.color_cyan, text_color=self.color_cyan)
            
        self.append_log(f"[Cognition Core]: Transitioned state to '{state.upper()}'")

    def _update_dialog_ui(self, text, is_user):
        self.txt_dialog.configure(state="normal")
        
        # Format tags / clean outputs
        if is_user:
            # Update real-time command display
            cleaned_text = text.replace("USER:", "").replace("USER (Typed):", "").strip()
            self.lbl_realtime_cmd.configure(text=cleaned_text, font=("Segoe UI", 10, "bold"), text_color="#FFF")
            
            # Format text log
            self.txt_dialog.insert(tk.END, "● USER: ", "user_tag")
            self.txt_dialog.insert(tk.END, cleaned_text + "\n\n")
        else:
            # Update real-time voice response display
            cleaned_text = text.replace("JARVIS:", "").strip()
            self.lbl_realtime_res.configure(text=cleaned_text, font=("Segoe UI", 10, "bold"), text_color=self.color_cyan)
            
            # Format text log
            self.txt_dialog.insert(tk.END, "◈ JARVIS: ", "jarvis_tag")
            self.txt_dialog.insert(tk.END, cleaned_text + "\n\n")
            
        self.txt_dialog.see(tk.END)
        self.txt_dialog.configure(state="disabled")

    def _update_log_ui(self, text):
        self.txt_logs.configure(state="normal")
        self.txt_logs.insert(tk.END, f"[{self._get_timestamp()}] {text}\n")
        self.txt_logs.see(tk.END)
        self.txt_logs.configure(state="disabled")

    def _get_timestamp(self):
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

    # =========================================================================
    # GLOWING SCI-FI HUD ARC REACTOR ANIMATION
    # =========================================================================
    
    def _animate_hud(self):
        """Animates dynamic vector graphic overlays and circles surrounding our CTkButton."""
        self.canvas.delete("all")
        
        # Dimensions
        cx, cy = 140, 140
        r_outer = 100
        r_middle = 80
        r_inner = 60
        
        # Determine pulsing attributes based on application state
        color = self.color_cyan
        pulse_speed = 0.05
        rotate_speed = 1.0
        
        if self.current_state == "idle":
            color = self.color_cyan
            pulse_speed = 0.04
            rotate_speed = 0.6
        elif self.current_state == "listening":
            color = self.color_amber
            pulse_speed = 0.12
            rotate_speed = 4.0
        elif self.current_state == "thinking":
            color = self.color_purple
            pulse_speed = 0.18
            rotate_speed = -2.5
        elif self.current_state == "speaking":
            color = self.color_cyan
            pulse_speed = 0.22
            rotate_speed = 1.2
            
        # Update animations metrics
        self.reactor_angle = (self.reactor_angle + rotate_speed) % 360
        self.pulse_phase = (self.pulse_phase + pulse_speed) % (2 * math.pi)
        
        pulse_factor = 0.82 + 0.18 * math.sin(self.pulse_phase)
        
        # Draw glowing halo rings (simulated neon via outer arc layers)
        outer_glow_r = r_outer + (10 * math.sin(self.pulse_phase))
        self.canvas.create_oval(cx - outer_glow_r, cy - outer_glow_r, cx + outer_glow_r, cy + outer_glow_r, outline="#122538", width=1)
        self.canvas.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer, outline=color, width=2)
        
        # Draw mechanical spinning ring ticks (dashboard HUD spokes)
        num_ticks = 12
        tick_step = 360 / num_ticks
        
        for i in range(num_ticks):
            deg = self.reactor_angle + (i * tick_step)
            rad = math.radians(deg)
            
            x1 = cx + (r_middle - 6) * math.cos(rad)
            y1 = cy + (r_middle - 6) * math.sin(rad)
            x2 = cx + (r_middle + 6) * math.cos(rad)
            y2 = cy + (r_middle + 6) * math.sin(rad)
            
            thickness = 2 if i % 3 == 0 else 1
            tick_color = color if i % 3 == 0 else "#253545"
            
            self.canvas.create_line(x1, y1, x2, y2, fill=tick_color, width=thickness)
            
        # Draw concentric boundary and dash orbits
        self.canvas.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner, outline="#1A2F45", width=1, dash=(8, 4))
        
        # Draw outer radar sweep
        self.canvas.create_arc(cx - r_outer - 12, cy - r_outer - 12, cx + r_outer + 12, cy + r_outer + 12, start=self.reactor_angle * 2, extent=80, outline="#2A455E", width=1, style="arc")
        self.canvas.create_arc(cx - r_outer - 12, cy - r_outer - 12, cx + r_outer + 12, cy + r_outer + 12, start=(self.reactor_angle * 2) + 180, extent=80, outline="#2A455E", width=1, style="arc")
        
        # Speaking dynamic voice wave overlays
        if self.current_state == "speaking":
            for r_wave in [r_outer + 18, r_outer + 30]:
                wave_amp = r_wave + (8 * math.sin(self.pulse_phase * 3))
                self.canvas.create_oval(cx - wave_amp, cy - wave_amp, cx + wave_amp, cy + wave_amp, outline=self.color_cyan, width=1, dash=(2, 6))
                
        # Re-schedule frame ticks (every 40ms)
        self.root.after(40, self._animate_hud)

    def _show_boot_animation(self):
        """Displays a spectacular cyberpunk sci-fi loading and boot animation."""
        self.boot_frame = ctk.CTkFrame(self.root, fg_color=self.color_obsidian, corner_radius=0)
        self.boot_frame.grid(row=0, column=0, sticky="nsew")
        self.boot_frame.grid_columnconfigure(0, weight=1)
        self.boot_frame.grid_rowconfigure(0, weight=4) # Canvas
        self.boot_frame.grid_rowconfigure(1, weight=1) # Progress bar
        self.boot_frame.grid_rowconfigure(2, weight=2) # Status logs
        
        # 1. Loading circular canvas
        self.boot_canvas = ctk.CTkCanvas(self.boot_frame, width=300, height=300, bg=self.color_obsidian, highlightthickness=0)
        self.boot_canvas.grid(row=0, column=0, pady=(40, 0))
        
        # 2. Boot progress bar
        self.boot_progress = ctk.CTkProgressBar(self.boot_frame, width=450, height=8, progress_color=self.color_cyan, fg_color="#1E293B")
        self.boot_progress.set(0.0)
        self.boot_progress.grid(row=1, column=0, pady=20)
        
        # 3. Boot logs label
        self.lbl_boot_status = ctk.CTkLabel(
            self.boot_frame,
            text="CORE INITIALIZATION SEQUENCE INITIATED...",
            font=("Consolas", 11, "bold"),
            text_color=self.color_cyan
        )
        self.lbl_boot_status.grid(row=2, column=0, pady=(0, 40))
        
        # Animating details
        self.boot_angle = 0
        self.boot_log_lines = [
            ">> INITIALIZING J.A.R.V.I.S. COGNITIVE SYNAPSE...",
            ">> LOADING AUTOMATION SKILLSETS & LOCAL OS BINDINGS [OK]",
            ">> EMITTING GOOGLE GEMINI NEURAL FALLBACK MIND [OK]",
            ">> CONNECTING SPEECH INTEGRATOR & CORE SYNTHESIS [OK]",
            ">> SYSTEM ONLINE. HELLO, SIR. SYSTEMS ARE FULLY SECURED."
        ]
        
        # Core animation loop for boot canvas
        def tick_boot_canvas():
            if not hasattr(self, 'boot_frame') or not self.boot_frame.winfo_exists():
                return
            self.boot_canvas.delete("all")
            cx, cy = 150, 150
            r1, r2, r3 = 100, 75, 50
            self.boot_angle = (self.boot_angle + 6) % 360
            
            # Spinning glowing circles
            self.boot_canvas.create_oval(cx - r1, cy - r1, cx + r1, cy + r1, outline="#002D33", width=2)
            self.boot_canvas.create_arc(cx - r1 - 5, cy - r1 - 5, cx + r1 + 5, cy + r1 + 5, start=self.boot_angle, extent=60, outline=self.color_cyan, width=3, style="arc")
            self.boot_canvas.create_arc(cx - r1 - 5, cy - r1 - 5, cx + r1 + 5, cy + r1 + 5, start=self.boot_angle + 180, extent=60, outline=self.color_cyan, width=3, style="arc")
            
            self.boot_canvas.create_arc(cx - r2, cy - r2, cx + r2, cy + r2, start=-self.boot_angle * 1.5, extent=100, outline=self.color_amber, width=2, style="arc")
            self.boot_canvas.create_oval(cx - r3, cy - r3, cx + r3, cy + r3, outline="#2A1B30", width=1, dash=(4, 4))
            
            # Glowing core reactor center
            r_pulse = 25 + 5 * math.sin(math.radians(self.boot_angle * 2))
            self.boot_canvas.create_oval(cx - r_pulse, cy - r_pulse, cx + r_pulse, cy + r_pulse, fill="#082A3A", outline=self.color_cyan, width=2)
            self.boot_canvas.create_text(cx, cy, text="J.A.R.V.I.S.", font=("Consolas", 8, "bold"), fill=self.color_cyan)
            
            self.root.after(30, tick_boot_canvas)
            
        tick_boot_canvas()
        
        # Step-by-step loading sequence
        def load_step(idx, progress):
            if idx < len(self.boot_log_lines):
                self.lbl_boot_status.configure(text=self.boot_log_lines[idx])
                self.boot_progress.set(progress)
                self.append_log(f"[Boot Sequence]: {self.boot_log_lines[idx]}")
                
                # Slower/faster delays to make it look realistic
                self.root.after(450, lambda: load_step(idx + 1, progress + 0.25))
            else:
                # Boot finished! Complete progress bar, say goodbye to boot frame, speak welcome
                self.boot_progress.set(1.0)
                self.root.after(300, complete_boot)
                
        def complete_boot():
            # Fade out/destroy the frame
            self.boot_frame.destroy()
            self.append_log("[Core Operations]: J.A.R.V.I.S. operating cockpit loaded at 100% efficiency.")
            
            # Broadcast verbal welcome via speech engine
            boot_welcome = "Systems online, sir. Cognitive layers are running at optimal capacity. How can I assist you?"
            self.append_dialog(f"JARVIS: {boot_welcome}", is_user=False)
            
            # Use callback to speak it safely on a worker thread
            if self.on_settings_change:
                import threading
                threading.Thread(target=lambda: self.on_settings_change("greet", None), daemon=True).start()
            
        # Start the loading steps
        self.root.after(200, lambda: load_step(0, 0.0))

    def _on_close(self):
        self.root.destroy()
        sys.exit()

class QueueLogHandler(logging.Handler):
    """Integrates logging messages directly into the CustomTkinter diagnostics console."""
    def __init__(self, gui_instance):
        super().__init__()
        self.gui = gui_instance
        
    def emit(self, record):
        log_entry = self.format(record)
        self.gui.append_log(log_entry)
