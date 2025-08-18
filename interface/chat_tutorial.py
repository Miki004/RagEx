from src.robbi import get_name, get_role, get_format, get_context, evaluate_prompt
from interface.chat import Chat

class ChatTutorial(Chat):
    
    def __init__(self, container):
        super().__init__(container)

        self.graph = State

        self.user_input.bind("<Return>", self._on_enter_pressed)
        
        self.next_button.configure(command=self.go_to_final_request)

        self.add_context_bubble("Tutorial: Impara a Comunicare con Robbi")
        self.after(1000, self.add_message_bubble("Come ti chiami?", is_user=False))
        self.after(1000, self.add_message_bubble("Scrivi il tuo messaggio nel riquadro arancione e premi invio per mandarlo.", is_user=False))


    def _on_enter_pressed(self, event):
        if event.state & 0x0001:  # Shift � premuto
            return  # Permetti il normale comportamento di andare a capo

        prompt = self.get_message_from_textbox()
        self.add_message_bubble(prompt, is_user=True)
        self.user_input.delete("1.0", "end")
        try:
            response = self.logic.process_input(prompt)
            self.add_message_bubble(response, is_user=False) # self.session.send_message(prompt)
        except Exception as e:
            self.user_input.destroy()
            self.add_error_bubble(f"Errore durante l'esecuzione del prompt finale: {str(e)}. Clicca il bottone per tornare alla pagina della storia e riprovare il tutorial!")
            self.next_button.configure(text='Torna indietro', command=self.go_to_story_page)
            self.next_button.pack(side='left', padx=20, pady=(0, 20), anchor='center')
        
        try:
            if self.logic.is_tutorial_completed():
                # Distruggi il frame di input
                self.user_input.destroy()
                self.add_recap_bubble(f"RECAP:\n"+self.logic.prompt_recap())
                final_prompt = self.logic.rewrite_prompt()
                self.add_recap_bubble(f"PROMPT IDEALE:\n"+final_prompt)
                response = self.logic.exec_prompt(final_prompt)
                self.add_message_bubble(f"OUTPUT:\n"+ response, is_user=False)
                self.add_message_bubble("È stato un piacere giocare con te!", is_user=False)
                self.next_button.pack(side='left', padx=20, pady=(0, 20), anchor='center')
        except Exception as e:
            self.add_error_bubble(f"Errore durante l'esecuzione del prompt finale: {str(e)}. Clicca il bottone per tornare alla pagina della storia e riprovare il tutorial!")
            self.next_button.configure(text='Torna indietro', command=self.go_to_story_page)
            self.next_button.pack(side='left', padx=20, pady=(0, 20), anchor='center')
        return "break"
    
