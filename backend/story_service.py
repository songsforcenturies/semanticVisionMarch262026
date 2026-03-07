"""
AI Story Generation Service for LexiMaster
Uses OpenAI GPT to generate educational narratives with embedded vocabulary
"""
import os
import json
from typing import List, Dict, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage


class StoryGenerationService:
    """Service for generating educational stories with AI"""
    
    def __init__(self):
        self.api_key = None
    
    def _get_api_key(self):
        """Lazy load API key"""
        if not self.api_key:
            self.api_key = os.environ.get('EMERGENT_LLM_KEY')
            if not self.api_key:
                raise ValueError("EMERGENT_LLM_KEY not found in environment")
        return self.api_key
    
    async def generate_story(
        self,
        student_name: str,
        student_age: int,
        grade_level: str,
        interests: List[str],
        prompt: str,
        baseline_words: List[Dict[str, str]],
        target_words: List[Dict[str, str]],
        stretch_words: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Generate a 5-chapter educational story
        
        Returns:
            {
                "title": str,
                "theme": str,
                "chapters": [
                    {
                        "number": int,
                        "title": str,
                        "content": str,
                        "word_count": int,
                        "embedded_tokens": [{"word": str, "tier": str}],
                        "vision_check": {
                            "question": str,
                            "options": [str],
                            "correct_index": int
                        }
                    }
                ]
            }
        """
        
        # Get API key
        api_key = self._get_api_key()
        
        # Prepare vocabulary lists
        baseline_list = [w['word'] for w in baseline_words]
        target_list = [w['word'] for w in target_words]
        stretch_list = [w['word'] for w in stretch_words]
        
        # Create the story generation prompt
        system_message = f"""You are an expert educational story writer for LexiMaster. 
Generate engaging, age-appropriate stories that naturally embed vocabulary words for learning.

Student Profile:
- Name: {student_name}
- Age: {student_age}
- Grade: {grade_level}
- Interests: {', '.join(interests)}

Vocabulary Distribution (MUST follow exactly):
- 60% BASELINE words (comfortable level): {baseline_list}
- 30% TARGET words (growth level): {target_list}
- 10% STRETCH words (challenge level): {stretch_list}

Requirements:
1. Create exactly 5 chapters
2. Each chapter should be 300-500 words
3. Naturally weave vocabulary throughout the story
4. Use each vocabulary word at least once
5. Make the story engaging and educational
6. Create a comprehension question for each chapter with 4 multiple-choice options

Story Theme: {prompt}"""

        user_prompt = f"""Generate a complete 5-chapter story for {student_name} based on: "{prompt}"

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
  "title": "Story Title Here",
  "theme": "Brief theme description",
  "chapters": [
    {{
      "number": 1,
      "title": "Chapter 1 Title",
      "content": "Full chapter text here...",
      "embedded_tokens": [
        {{"word": "planet", "tier": "baseline"}},
        {{"word": "gravity", "tier": "target"}}
      ],
      "vision_check": {{
        "question": "What did the character discover?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_index": 0
      }}
    }}
  ]
}}

Remember: Use vocabulary naturally, make it engaging, and ensure comprehension questions test understanding!"""

        try:
            # Initialize LLM chat
            chat = LlmChat(
                api_key=api_key,
                session_id=f"story_gen_{student_name}",
                system_message=system_message
            )
            
            # Use GPT-5.2 for best results
            chat.with_model("openai", "gpt-5.2")
            
            # Send message and get response
            message = UserMessage(text=user_prompt)
            response = await chat.send_message(message)
            
            # Parse JSON response
            story_data = json.loads(response)
            
            # Calculate word counts and validate
            for chapter in story_data.get("chapters", []):
                chapter["word_count"] = len(chapter.get("content", "").split())
            
            # Add total word count
            story_data["total_word_count"] = sum(
                ch.get("word_count", 0) for ch in story_data.get("chapters", [])
            )
            
            return story_data
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return error
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Story generation failed: {str(e)}")


# Initialize service
story_service = StoryGenerationService()
