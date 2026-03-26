"""
AI Story Generation Service for Semantic Vision
Supports OpenRouter for flexible model selection
"""
import os
import json
import time
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI


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
            self.api_key = os.environ.get('OPENROUTER_API_KEY')
            if not self.api_key:
                raise ValueError("OPENROUTER_API_KEY not found in environment")
        return self.api_key
    
    async def _get_llm_config(self):
        """Get current LLM configuration"""
        if self.db is not None:
            config = await self.db.system_config.find_one({"key": "llm_config"}, {"_id": 0})
            if config and config.get("value"):
                return config["value"]
        return {"provider": "openrouter", "model": "openai/gpt-4o-mini"}
    
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
        cultural_context: Any = "",
        custom_heritage: str = "",
        culture_learning: List[str] = [],
        language: str = "English",
        brand_placements: List[Dict[str, Any]] = [],
        media_placements: List[Dict[str, Any]] = [],
        strengths: str = "",
        weaknesses: str = "",
    ) -> Dict[str, Any]:
        """Generate a 5-chapter educational story"""
        
        start_time = time.time()
        llm_config = await self._get_llm_config()
        provider = llm_config.get("provider", "openrouter")
        model = llm_config.get("model", "gpt-5.2")
        
        # Get API key
        api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
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
        # Handle array or string cultural_context
        heritage_items = cultural_context if isinstance(cultural_context, list) else ([cultural_context] if cultural_context else [])
        if custom_heritage:
            heritage_items.extend([h.strip() for h in custom_heritage.split(',') if h.strip()])
        if heritage_items:
            heritage_str = ', '.join(heritage_items)
            culture_section = f"""
CULTURAL CONTEXT: Incorporate culturally relevant elements from these heritages: {heritage_str}.
Include names, settings, traditions, foods, or customs that resonate with these cultural backgrounds.
Ensure respectful and authentic representation."""

        # Culture learning topics
        culture_learning_section = ""
        if culture_learning:
            TOPIC_LABELS = {
                'black_history': 'Black History & Culture — African American heritage, leaders, and contributions',
                'black_women': 'Black Women in History — trailblazing Black women and their achievements',
                'hispanic_heritage': 'Hispanic Heritage — Latino/Latina culture, traditions, and leaders',
                'asian_pacific': 'Asian & Pacific Islander Heritage — diverse cultures across Asia and the Pacific',
                'native_american': 'Native American Heritage — Indigenous peoples, traditions, and history',
                'womens_history': "Women's History — women who changed the world across cultures",
                'african_culture': 'African Culture & History — rich traditions across the African continent',
                'middle_eastern': 'Middle Eastern Culture — ancient civilizations, art, and modern contributions',
                'european_history': 'European History & Culture — traditions, inventions, and diversity',
                'caribbean_culture': 'Caribbean Culture — island traditions, music, food, and stories',
                'lgbtq_history': 'LGBTQ+ History — stories of courage, identity, and acceptance',
                'disability_awareness': 'Disability Awareness — celebrating abilities and understanding differences',
                'world_religions': 'World Religions & Spirituality — understanding different faith traditions',
                'stem_pioneers': 'STEM Pioneers of Color — scientists and innovators from diverse backgrounds',
                'civil_rights': 'Civil Rights Movement — the fight for equality and justice',
                'immigration_stories': 'Immigration Stories — journeys of courage and new beginnings',
            }
            topics = [TOPIC_LABELS.get(t, t) for t in culture_learning]
            culture_learning_section = f"""
CULTURE LEARNING FOCUS: The parent specifically wants this story to incorporate educational elements about:
{chr(10).join('- ' + t for t in topics)}
Weave in historical facts, notable figures, and cultural knowledge naturally into the story."""

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

        # Digital media section
        media_section = ""
        if media_placements:
            media_items = []
            for mp in media_placements:
                mtype = mp.get("media_type", "audio")
                desc = f"- \"{mp['title']}\" by {mp.get('artist', 'Unknown')} ({mtype})"
                media_items.append(desc)
            media_section = f"""
DIGITAL MEDIA INTEGRATION: Naturally embed references to these songs/videos into the story at moments where music or media would enhance the experience.
When the character encounters a moment of inspiration, celebration, learning, or reflection, mention one of these songs/videos as something the character hears, discovers, or is reminded of.
Format each media reference in the story text as: [MEDIA:media_id:title] — this will be rendered as a playable media element.
Available media:
{chr(10).join(media_items)}
Media IDs: {', '.join(f"{mp['id']}" for mp in media_placements)}
Include 1-2 media references across the story, making them feel organic to the narrative."""

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
        # Grade-level complexity mapping for age-appropriate language
        grade_complexity = {
            "pre-k": "very simple sentences, 3-5 word vocabulary, familiar everyday objects and animals",
            "k": "simple sentences, basic sight words, concrete concepts, repetition for learning",
            "1": "short sentences, common vocabulary, basic story structure, simple cause and effect",
            "2": "developing sentences, grade 2 vocabulary, beginning chapter books level",
            "3": "moderate sentence complexity, grade 3 vocabulary, descriptive language",
            "4": "compound sentences, grade 4 vocabulary, figurative language introduction",
            "5": "complex sentences, grade 5 vocabulary, abstract concepts, inference skills",
            "6": "middle school vocabulary, complex narrative structure, themes and symbolism",
            "7": "advanced vocabulary, multi-layered narratives, critical thinking prompts",
            "8": "sophisticated vocabulary, nuanced characters, complex moral dilemmas",
            "9": "high school vocabulary, literary techniques, analytical thinking",
            "10": "advanced literary vocabulary, complex themes, persuasive reasoning",
            "11": "college-prep vocabulary, advanced literary analysis, rhetorical strategies",
            "12": "college-level vocabulary, sophisticated narrative structure, philosophical themes",
            "college": "academic vocabulary, complex argumentation, interdisciplinary concepts",
            "adult": "professional vocabulary, nuanced storytelling, real-world complexity",
        }
        complexity_guide = grade_complexity.get(str(grade_level), grade_complexity.get("5", "moderate complexity"))

        brand_question_section = ""
        if brand_placements:
            brand_names = [bp['name'] for bp in brand_placements]
            brand_question_section = f"""
BRAND COMPREHENSION: For at least one chapter that features a brand product, the comprehension question MUST test the student's understanding of HOW the brand's product helped solve a problem in the story. Reference the brand or product by name in the question or answer options. These are 'Brand Activation Questions' — they measure whether the student understood the role of the product in the narrative. Brands featured: {', '.join(brand_names)}."""

        system_message = f"""You are an expert educational story writer for Semantic Vision. 
Generate engaging, age-appropriate stories that naturally embed vocabulary words for learning.

Student Profile:
- Name: {student_name}
- Age: {student_age}
- Grade: {grade_level}
- Interests: {', '.join(interests)}
- Character Lessons: {', '.join(virtues) if virtues else 'General positive values'}

GRADE-LEVEL LANGUAGE GUIDE: Write at a complexity appropriate for grade {grade_level}: {complexity_guide}. 
The comprehension questions and answer choices must also match this reading level.
Vocabulary words from the word banks may be above grade level (that is intentional for learning) but the surrounding narrative text, sentence structure, and comprehension questions should be appropriate for a {grade_level} reader aged {student_age}.

Vocabulary Distribution:
- 60% BASELINE words: {baseline_list}
- 30% TARGET words: {target_list}
- 10% STRETCH words: {stretch_list}

{f"CHARACTER EDUCATION: Weave lessons about {', '.join(virtues)} into the story." if virtues else ""}
{belief_section}
{culture_section}
{culture_learning_section}
{language_section}
{brand_section}
{brand_question_section}
{media_section}
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
            # Use OpenAI client with OpenRouter base URL
            client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                default_headers={"HTTP-Referer": "https://semanticvision.ai"},
                max_retries=1,
                timeout=60.0,
            )
            # Some free models don't support system messages, merge into user message
            merged_prompt = f"{system_message}\n\n---\n\n{user_prompt}"

            # Try with retries and fallback models
            fallback_models = [
                model,
                "openai/gpt-4o-mini",
                "google/gemma-3-27b-it:free",
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
