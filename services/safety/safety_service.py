class SafetyService:
    def check_message(self, message: str) -> dict:
        # MVP basic safety check. 
        # In a real app, this might use an LLM or predefined lists.
        lower_msg = message.lower()
        crisis_keywords = ["suicide", "kill myself", "self harm", "end it all"]
        emotional_keywords = ["lonely", "depressed", "sad", "stressed", "anxious", "difficult day"]
        
        for word in crisis_keywords:
            if word in lower_msg:
                return {
                    "is_safe": False,
                    "level": "crisis",
                    "response": "I'm really sorry you're feeling this way, but I'm an AI and can't provide the help you need. Please consider reaching out to a crisis helpline, emergency services, or someone you trust immediately. Your life has value."
                }
                
        for word in emotional_keywords:
            if word in lower_msg:
                return {
                    "is_safe": True,
                    "level": "emotional_support",
                    "instruction": "The user is expressing emotional distress. Be extremely empathetic, supportive, and conversational. Do not claim to be a human therapist. Encourage real-world support if it seems appropriate. Keep it concise."
                }
                
        return {
            "is_safe": True,
            "level": "normal"
        }

safety_service = SafetyService()
