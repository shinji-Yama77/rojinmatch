import random

class ShisaService:
    """
    Service for interacting with Shisa.AI models.
    Currently mocks the interaction as we don't have a live API key.
    """
    def __init__(self):
        # In the future, this would connect to a hosted Shisa model (e.g. via OpenRouter or vLLM)
        self.model_name = "shisa-v2.1-70b"
        
    def get_welcome_message(self) -> str:
        """Returns a welcome message in Japanese, representing Shisa's persona."""
        messages = [
            "老人マッチへようこそ。シーサーAIが、あなたにぴったりの話し相手をお探しします。少々お待ちください。",
            "こんにちは。老人マッチです。現在、パートナーを検索中です。音楽を聴きながらお待ちください。",
            "お電話ありがとうございます。シーサーAIです。素敵な出会いがあるまで、少しだけお待ちくださいね。"
        ]
        return random.choice(messages)

    async def check_safety(self, text: str) -> bool:
        """
        Analyze text for safety using Shisa model.
        Returns True if safe, False if unsafe.
        """
        # Mock implementation: checking for keywords locally
        # In production, this would call the Shisa API for nuanced analysis
        unsafe_keywords = [
            "unsafe", "help", "bank", "money", "scam", "fraud",
            "助けて", "銀行", "お金", "詐欺", "怖い", "警察"
        ]
        if any(keyword in text.lower() for keyword in unsafe_keywords):
            return False
        return True

shisa_service = ShisaService()
