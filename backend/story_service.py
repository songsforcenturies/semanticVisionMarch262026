"""
AI Story Generation Service for Semantic Vision
Supports Emergent LLM Key and OpenRouter for flexible model selection
"""
import os
import json
import time
from typing import List, Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage


class StoryGenerationService:
    """Service for generating educational stories with AI"""
    
    def __init__(self):
        self.api_key = None
        self.db = None
    
    def set_db(self, db):
        """Set database reference for cost logging"""
        self.db = db
    
    def _get_api_key(self):
        """Lazy load API key"""
        if not self.api_key:
            self.api_key = os.environ.get('EMERGENT_LLM_KEY')
            if not self.api_key:
                raise ValueError("EMERGENT_LLM_KEY not found in environment")
        return self.api_key
    
    async def _get_llm_config(self):
        """Get current LLM configuration"""
        if self.db is not None:
            config = await self.db.system_config.find_one({"key": "llm_config"}, {"_id": 0})
            if config and config.get("value"):
                return config["value"]
        return {"provider": "emergent", "model": "gpt-5.2"}
    
    async def _log_cost(self, student_id: str, student_name: str, guardian_id: str, 
                        guardian_name: str, model: str, provider: str,
                        prompt_tokens: int, completion_tokens: int,
                        duration_seconds: float, success: bool):
        """Log LLM usage cost to database"""
        if self.db is None:
            return
        
        # Estimate cost based on model
        cost_per_1k_input = 0.01  # default
        cost_per_1k_output = 0.03
        
        cost_map = {
            "gpt-5.2": (0.01, 0.03),
            "gpt-4o": (0.0025, 0.01),
            "gpt-4o-mini": (0.00015, 0.0006),
            "meta-llama/llama-3.3-70b-instruct:free": (0, 0),
            "google/gemma-3-27b-it:free": (0, 0),
            "deepseek/deepseek-r1-0528:free": (0, 0),
            "nvidia/llama-3.1-nemotron-ultra-253b:free": (0, 0),
            "openrouter/auto": (0.001, 0.003),
        }
        if model in cost_map:
            cost_per_1k_input, cost_per_1k_output = cost_map[model]
        elif ":free" in model:
            cost_per_1k_input, cost_per_1k_output = 0, 0
        
        estimated_cost = (prompt_tokens / 1000 * cost_per_1k_input) + (completion_tokens / 1000 * cost_per_1k_output)
        
        log_entry = {
            "id": str(__import__('uuid').uuid4()),
            "student_id": student_id,
            "student_name": student_name,
            "user_id": guardian_id,
            "user_name": guardian_name,
            "model": model,
            "provider": provider,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "estimated_cost": round(estimated_cost, 6),
            "duration_seconds": round(duration_seconds, 2),
            "success": success,
            "type": "story_generation",
            "created_date": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        }
        await self.db.cost_logs.insert_one(log_entry)
        return estimated_cost

    async def generate_story(
        self,
        student_name: str,
        student_age: int,
        grade_level: str,
        interests: List[str],
        prompt: str,
        baseline_words: List[Dict[str, str]],
        target_words: List[Dict[str, str]],
        stretch_words: List[Dict[str, str]],
        virtues: List[str] = [],
        student_id: str = "",
        guardian_id: str = "",
        guardian_name: str = "",
        belief_system: str = "",
        cultural_context: str = "",
        language: str = "English",
        brand_placements: List[Dict[str, Any]] = [],
        strengths: str = "",
        weaknesses: str = "",
    ) -> Dict[str, Any]:
        """Generate a 5-chapter educational story"""
        
        start_time = time.time()
        llm_config = await self._get_llm_config()
        provider = llm_config.get("provider", "emergent")
        model = llm_config.get("model", "gpt-5.2")
        
        # Get API key
        if provider == "openrouter":
            api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OpenRouter API key not configured")
        else:
            api_key = self._get_api_key()
        
        # Prepare vocabulary lists
        baseline_list = [w['word'] for w in baseline_words]
        target_list = [w['word'] for w in target_words]
        stretch_list = [w['word'] for w in stretch_words]
        
        # Build belief/culture prompt sections
        belief_section = ""
        if belief_system:
            belief_section = f"""
BELIEF SYSTEM & VALUES: The story should reflect the values and teachings of {belief_system}.
Characters should demonstrate behaviors and decision-making consistent with {belief_system} principles.
Show how a person following {belief_system} would navigate the story's challenges with wisdom and virtue."""
        
        culture_section = ""
        if cultural_context:
            culture_section = f"""
CULTURAL CONTEXT: Incorporate culturally relevant elements from {cultural_context} culture.
Include names, settings, traditions, foods, or customs that resonate with {cultural_context} heritage.
Ensure respectful and authentic representation."""

        language_section = ""
        if language and language.lower() != "english":
            language_section = f"""
LANGUAGE: Write the ENTIRE story in {language}. All chapter titles, content, and vocabulary explanations must be in {language}."""

        brand_section = ""
        if brand_placements:
            brand_items = []
            for bp in brand_placements:
                products = bp.get("products", [])
                prod_names = [p.get("name", "") for p in products if p.get("name")]
                problem = bp.get("problem_statement", "")
                logo = bp.get("logo_url", "")
                desc = f"- {bp['name']}"
                if problem:
                    desc += f" (solves: {problem})"
                if prod_names:
                    desc += f" — products: {', '.join(prod_names)}"
                if logo:
                    desc += f" [logo: {logo}]"
                brand_items.append(desc)
            brand_section = f"""
BRAND INTEGRATION: Naturally weave these brands into the story as helpful solutions to problems the characters face.
Focus on how each brand's products solve a real problem relevant to the story.
Make brand mentions feel organic and educational, not like advertisements.
{chr(10).join(brand_items)}
Include 1-2 natural brand mentions across the story where they solve a problem or help the character learn."""

        # Build strengths & weaknesses prompt section
        strengths_section = ""
        if strengths or weaknesses:
            strengths_section = "\nSTRENGTHS & GROWTH AREAS:"
            if strengths:
                strengths_section += f"""
CHILD'S STRENGTHS: {strengths}
The protagonist should exhibit and celebrate these strengths. Show the character using these abilities as superpowers to help others, solve problems, and lead. Reinforce that these strengths are valuable and worth developing further."""
            if weaknesses:
                strengths_section += f"""
CHILD'S GROWTH AREAS: {weaknesses}
The protagonist should face challenges related to these areas. Show the character struggling with but GROWING through these challenges. Weave in practical strategies and small victories. The story should model how to improve in these areas through perseverance, support from others, and positive mindset — never shame or deficit framing. Show that growth is possible and celebrate progress over perfection."""

        # Create the story generation prompt
        system_message = f"""You are an expert educational story writer for Semantic Vision. 
Generate engaging, age-appropriate stories that naturally embed vocabulary words for learning.

Student Profile:
- Name: {student_name}
- Age: {student_age}
- Grade: {grade_level}
- Interests: {', '.join(interests)}
- Character Lessons: {', '.join(virtues) if virtues else 'General positive values'}

Vocabulary Distribution:
- 60% BASELINE words: {baseline_list}
- 30% TARGET words: {target_list}
- 10% STRETCH words: {stretch_list}

{f"CHARACTER EDUCATION: Weave lessons about {', '.join(virtues)} into the story." if virtues else ""}
{belief_section}
{culture_section}
{language_section}
{brand_section}
{strengths_section}

Requirements:
1. Create exactly 5 chapters, each 300-500 words
2. Naturally weave vocabulary throughout
3. Use each vocabulary word at least once
4. Create a comprehension question per chapter with 4 options
{f"5. Show protagonist learning {', '.join(virtues[:2])}" if virtues else ""}

Story Theme: {prompt}"""

        user_prompt = f"""Generate a 5-chapter story for {student_name} about: "{prompt}"

Return ONLY valid JSON (no markdown):
{{
  "title": "Story Title",
  "theme": "Brief theme",
  "chapters": [
    {{
      "number": 1,
      "title": "Chapter Title",
      "content": "Full chapter text...",
      "embedded_tokens": [{{"word": "example", "tier": "baseline"}}],
      "vision_check": {{
        "question": "Comprehension question?",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0
      }}
    }}
  ]
}}"""

        prompt_tokens_est = len(system_message.split()) + len(user_prompt.split())
        
        try:
            if provider == "openrouter":
                # Use OpenAI client with OpenRouter base URL
                from openai import AsyncOpenAI
                client = AsyncOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                    default_headers={"HTTP-Referer": "https://leximaster.app"},
                    max_retries=1,
                    timeout=60.0,
                )
                # Some free models don't support system messages, merge into user message
                merged_prompt = f"{system_message}\n\n---\n\n{user_prompt}"
                
                # Try with retries and fallback models
                fallback_models = [
                    model,
                    "qwen/qwen3-next-80b-a3b-instruct:free",
                    "openai/gpt-oss-120b:free",
                    "nvidia/nemotron-nano-9b-v2:free",
                ]
                last_error = None
                for attempt_model in fallback_models:
                    try:
                        response = await client.chat.completions.create(
                            model=attempt_model,
                            messages=[
                                {"role": "user", "content": merged_prompt}
                            ],
                            temperature=0.8,
                            max_tokens=8000,
                        )
                        choice = response.choices[0]
                        response_text = choice.message.content or ""
                        # Some models use reasoning field instead of content
                        if not response_text and hasattr(choice.message, 'reasoning'):
                            response_text = choice.message.reasoning or ""
                        if not response_text:
                            raise ValueError("Empty response from model")
                        model = attempt_model  # Record actual model used
                        completion_tokens_est = len(response_text.split())
                        last_error = None
                        break
                    except Exception as e:
                        last_error = e
                        continue
                
                if last_error:
                    raise last_error
            else:
                # Use Emergent LLM integration
                chat = LlmChat(
                    api_key=api_key,
                    session_id=f"story_gen_{student_name}_{int(time.time())}",
                    system_message=system_message
                )
                chat.with_model("openai", model)
                message = UserMessage(text=user_prompt)
                response_text = await chat.send_message(message)
                completion_tokens_est = len(response_text.split())
            
            # Parse JSON response - handle markdown code blocks
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
            
            story_data = json.loads(text)
            
            # Calculate word counts
            for chapter in story_data.get("chapters", []):
                chapter["word_count"] = len(chapter.get("content", "").split())
            
            story_data["total_word_count"] = sum(
                ch.get("word_count", 0) for ch in story_data.get("chapters", [])
            )
            story_data["model_used"] = model
            story_data["provider_used"] = provider
            
            duration = time.time() - start_time
            
            # Log cost
            cost = await self._log_cost(
                student_id=student_id, student_name=student_name,
                guardian_id=guardian_id, guardian_name=guardian_name,
                model=model, provider=provider,
                prompt_tokens=prompt_tokens_est, completion_tokens=completion_tokens_est,
                duration_seconds=duration, success=True
            )
            if cost is not None:
                story_data["estimated_cost"] = round(cost, 6)
            
            return story_data
            
        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            await self._log_cost(
                student_id=student_id, student_name=student_name,
                guardian_id=guardian_id, guardian_name=guardian_name,
                model=model, provider=provider,
                prompt_tokens=prompt_tokens_est, completion_tokens=0,
                duration_seconds=duration, success=False
            )
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            duration = time.time() - start_time
            await self._log_cost(
                student_id=student_id, student_name=student_name,
                guardian_id=guardian_id, guardian_name=guardian_name,
                model=model, provider=provider,
                prompt_tokens=prompt_tokens_est, completion_tokens=0,
                duration_seconds=duration, success=False
            )
            raise Exception(f"Story generation failed: {str(e)}")


# Initialize service
story_service = StoryGenerationService()
