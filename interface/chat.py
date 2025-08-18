from interface.style import Style

import customtkinter as ctk
from PIL import Image
import tkinter as tk

class Chat(ctk.CTkFrame):
    def __init__(self, container):
        super().__init__(container, fg_color=Style.WINDOW_BG)

        self.message_bubbles = []
        self.last_user_message = None

        self.chat = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat.pack(fill="both",expand=True)

        self.input_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        self.input_frame.pack(fill="x", padx=20, pady=(0, 20), side="bottom")

        self.robby_img = ctk.CTkImage(
            light_image=Image.open("./rsc/robot.png").resize(
                (120, 120)
            ),
            size=(120, 120)
        )
        self.robby_label = ctk.CTkLabel(
            self.input_frame,
            image=self.robby_img,
            text=""
        )
        self.robby_label.pack(side="left")

        self.user_input = ctk.CTkTextbox(
            self.input_frame,
            font=Style.WIDGETS_FONT,
            fg_color=Style.WIDGETS_BG,
            height=120,
            text_color=Style.WIDGETS_FG_TEXT_COLOR,
            border_color=Style.WIDGETS_BORDER_COLOR,
            border_width=2,  # Ensure border is visible
            corner_radius=15
        )
        self.user_input.pack(side='left', fill='x', expand=True)

        self.next_button = ctk.CTkButton(
            self.input_frame,
            text="Prossimo",
            # command=self.go_to_recap_page,
            fg_color=Style.WIDGETS_BG,
            text_color=Style.WIDGETS_FG_TEXT_COLOR,
            border_color=Style.WIDGETS_BORDER_COLOR,
            border_width=2,
            corner_radius=15,
            height=70
        )

    def change_input_field_with_button(self):
        """Changes the input field to a button for the next phase."""

        # TODO: Destroy the input frame to remove the textbox and robot image

        self.next_button.pack(side='left', fill='x', expand=True)

    def get_message_from_textbox(self):
        """Handles sending a message from the user input."""
        user_message = self.user_input.get("1.0", "end-1c").strip() # Get the text from the textbox and strip whitespace
        
        self.user_input.delete # deleting the text from the textbox
        return user_message
    
    def add_error_bubble(self, message):
        """Adds an error message bubble to the chat interface."""
        bubble_frame = tk.Frame(self.chat, bg=Style.WINDOW_BG)
        bubble_frame.pack(fill='x', expand=True)

        bubble = ctk.CTkLabel(
            bubble_frame,
            text=message,
            fg_color=Style.ERROR_BUBBLE_COLOR,
            text_color=Style.WIDGETS_FG_TEXT_COLOR,
            font=Style.WIDGETS_FONT,
            wraplength=300,
            justify="left",
            corner_radius=15
        )
        bubble.pack(pady=(10, 0), padx=20)
        self.message_bubbles.append(bubble)
        self.chat.update_idletasks()
        self.chat._parent_canvas.yview_moveto(1.0)

    def add_context_bubble(self, message):
        """Adds an error message bubble to the chat interface."""
        bubble_frame = tk.Frame(self.chat, bg=Style.WINDOW_BG)
        bubble_frame.pack(fill='x', expand=True)

        bubble = ctk.CTkLabel(
            bubble_frame,
            text=message,
            fg_color=Style.CONTEXT_BUBBLE_COLOR,
            text_color=Style.WIDGETS_FG_TEXT_COLOR,
            font=Style.WIDGETS_FONT,
            wraplength=300,
            justify="left",
            corner_radius=15
        )
        bubble.pack(pady=(10, 0), padx=20)
        self.message_bubbles.append(bubble)
        self.chat.update_idletasks()
        self.chat._parent_canvas.yview_moveto(1.0)

    def add_message_bubble(self, message, is_user=True):
        """Adds a message bubble to the chat interface."""
        side = "right" if is_user else "left"

        bubble_frame = tk.Frame(self.chat, bg=Style.WINDOW_BG)
        bubble_frame.pack(fill='x', expand=True)

        bubble = ctk.CTkLabel(
            bubble_frame,
            text=message,
            fg_color=Style.USER_BUBBLE_BG if is_user else Style.ROBBY_BUBBLE_BG,
            text_color=Style.WIDGETS_FG_TEXT_COLOR,
            font=Style.WIDGETS_FONT,
            wraplength=300,
            justify="left",
            corner_radius=15
        )
        bubble.pack(side=side, pady=(10, 0), padx=20)
        self.message_bubbles.append(bubble)
        self.chat.update_idletasks()
        self.chat._parent_canvas.yview_moveto(1.0)

    def add_recap_bubble(self, message):
        """Adds a message bubble to the chat interface."""

        bubble_frame = tk.Frame(self.chat, bg=Style.WINDOW_BG)
        bubble_frame.pack(fill='x', expand=True)

        bubble = ctk.CTkLabel(
            bubble_frame,
            text=message,
            fg_color=Style.CONTEXT_BUBBLE_COLOR,
            text_color=Style.WIDGETS_FG_TEXT_COLOR,
            font=Style.WIDGETS_FONT,
            wraplength=300,
            justify="left",
            corner_radius=15
       )
        bubble.pack(side='left', pady=(10, 0), padx=20)
        self.message_bubbles.append(bubble)
        self.chat.update_idletasks()
        self.chat._parent_canvas.yview_moveto(1.0)
        