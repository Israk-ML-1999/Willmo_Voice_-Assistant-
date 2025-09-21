import os
import openai
from dotenv import load_dotenv
from .request import micro_goal_response
from app.config import settings


load_dotenv()

class Micro_goal:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=settings.OPENAI_API_BASE
        )

    def create_daily_plan(self, input_data: dict) -> micro_goal_response:
        prompt = self.create_prompt(input_data)
        response = self.get_ai_response(prompt)
        return response

    def create_prompt(self, input_data: dict) -> str:
            return f"""You are an AI assistant specialized in creating personalized micro goals for one day. Your task is to generate a daily plan based on the user's information, ensuring the content is age-appropriate and actionable.

            **Age Safety & Style:**
            - Ages 0–12: Fun, friendly, educational. Allowed: school topics, homework, daily life, simple games. Forbid: job tips, career advice, interview prep, adult topics.
            - Ages 13–17: Practical, motivational, study-focused personal growth; general job tips/interview basics/resume tips allowed. Avoid adult-specific content (e.g., sexual content). Health/fitness → only general, safe guidance.
            - Ages 18+: Professional, goal-oriented, personalized; allowed: career development, interview prep, personal development, fitness/health goals.

            **CRITICAL: Task Uniqueness Requirements:**
            - NEVER repeat or suggest tasks that are already in the past tasks list
            - Each generated task MUST be completely different from previous suggestions
            - If a similar concept was used before, find a different approach or angle
            - Be creative and innovative with new task suggestions
            - Review the past tasks carefully before generating new ones

            **Planning Instructions:**
            1) Analyze: user age, current state (mind, soul, body, purpose, spirituality, etc.), and the Big Goal.
            2) Review past tasks: {input_data['tasks']} - AVOID all of these completely.
            3) Generate: EXACTLY 5 NEW, UNIQUE daily micro plans aligned to the Big Goal.
            4) Verify: Each task is completely different from past suggestions.
            5) Ensure: age-appropriate, actionable tasks that haven't been suggested before.
            6) Balance: include tasks that reflect mind, soul/spirituality, and body when relevant.
            7) Assign categories: "mind" for learning/skills, "soul" for emotional/spiritual, "body" for physical health.
            8) Output: ONLY JSON (no extra text), short and clear.

            **JSON Output Contract (strict):**
            {{
            "big_goal": "{input_data['big_goal']}",
            "day_plan": [
                {{ "category": "mind", "title": "Skill Focus", "goal": "<string>"}},
                {{ "category": "soul", "title": "Calm Focus", "goal": "<string>" }},
                {{ "category": "body", "title": "Healthy Energy", "goal": "<string>" }},
                {{ "category": "mind", "title": "Application Step", "goal": "<string>" }},
                {{ "category": "soul", "title": "Positive Spirit", "goal": "<string>" }}
            ]
            }}

            **Personalization Data:**
            - big_goal: {input_data['big_goal']}
            - age: {input_data['age']}
            - userdata: {input_data['userdata']}
            - past tasks to AVOID: {input_data['tasks']}

            **MANDATORY RULES:**
            1. NEVER suggest tasks that appear in the past tasks list
            2. Each task must be completely new and unique
            3. Be creative and think of alternative approaches to support the big goal
            4. Tasks must be age-appropriate and actionable
            5. Maintain balance between mind, body, and soul/spirituality when relevant
            6. If you're running out of ideas, think of different contexts, methods, or perspectives

            **Return ONLY the JSON object above. No additional commentary.**

            Create a completely NEW personalized daily plan with tasks that have NEVER been suggested before.
            """


    def get_ai_response(self, prompt: str) -> micro_goal_response:
        import json
        from fastapi import HTTPException
        import re

        completion = self.client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=700
        )
        response_text = completion.choices[0].message.content.strip()
        
        try:
            # Remove markdown code blocks if present
            response_text = re.sub(r'^```(?:json)?\s*', '', response_text, flags=re.MULTILINE)
            response_text = re.sub(r'\s*```$', '', response_text, flags=re.MULTILINE)
            
            # Clean up whitespace and newlines
            response_text = response_text.encode('utf-8').decode('utf-8-sig')
            response_text = re.sub(r'[\r\n\t]', '', response_text)

            # Ensure proper JSON boundaries
            if not response_text.startswith('{'): 
                response_text = '{' + response_text
            if not response_text.endswith('}'): 
                response_text = response_text + '}'

            response_dict = json.loads(response_text)
            
            if not isinstance(response_dict, dict):
                raise ValueError("Response is not a dictionary")
            if 'big_goal' not in response_dict:
                raise ValueError("Missing 'big_goal' field")
            if 'day_plan' not in response_dict:
                raise ValueError("Missing 'day_plan' field")
            if not isinstance(response_dict['day_plan'], list):
                raise ValueError("'day_plan' is not a list")

            return micro_goal_response(**response_dict)
            
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {response_text}")
            raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"Invalid response structure: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing response: {str(e)}")
