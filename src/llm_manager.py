"""
Gemini LLM Manager with Rate Limiting
Optimized for Free Tier
"""

import time
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
# FIXED IMPORT - Updated path
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
from config import settings
from utils.rate_limiter import rate_limiter


class GeminiLLMManager:
    """Manage Gemini API calls with rate limiting"""
    
    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self.llm = None
        self.api_key_valid = False
        
        logger.info(f"Initializing Gemini LLM: {self.model_name}")
        
        # Check if API key is available
        if not settings.validate_api_key():
            logger.warning("⚠️  Gemini API key not configured. LLM features will be disabled.")
            logger.warning("Get your FREE key: https://makersuite.google.com/app/apikey")
            return
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=settings.TEMPERATURE,
                max_output_tokens=settings.MAX_OUTPUT_TOKENS,
                top_p=settings.TOP_P,
                top_k=settings.TOP_K
            )
            self.api_key_valid = True
            logger.info("✅ Gemini LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}")
            self.api_key_valid = False
    
    def generate_response(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response with rate limiting"""
        
        # Check if LLM is available
        if not self.api_key_valid or self.llm is None:
            return """
⚠️ **Gemini API Key Not Configured**

To use the AI response generation:
1. Get your FREE API key from: https://makersuite.google.com/app/apikey
2. Add it to your .env file: `GOOGLE_API_KEY=your_key_here`
3. Restart the application

**Your retrieved context is still available below! ⬇️**

---

**Context Found:**
""" + context[:500] + "..."
        
        # Acquire rate limit permission
        if not rate_limiter.acquire(timeout=30):
            logger.error("Rate limit exceeded, request blocked")
            return "⚠️ Rate limit exceeded. Please wait a moment and try again."
        
        try:
            # Build messages
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            user_message = f"""
Context Information:
{context}

User Question:
{query}

Please provide a comprehensive answer based on the context provided.
If the context doesn't contain relevant information, state that clearly.
"""
            messages.append(HumanMessage(content=user_message))
            
            # Generate response
            start_time = time.time()
            response = self.llm.invoke(messages)
            generation_time = time.time() - start_time
            
            logger.info(f"Response generated in {generation_time:.2f}s")
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"⚠️ Error generating response: {str(e)}"
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get current rate limit statistics"""
        if not self.api_key_valid:
            return {
                "minute_used": 0,
                "minute_limit": 0,
                "day_used": 0,
                "day_limit": 0,
                "minute_remaining": 0,
                "day_remaining": 0
            }
        return rate_limiter.get_stats()


# Global LLM manager instance
llm_manager = GeminiLLMManager()
