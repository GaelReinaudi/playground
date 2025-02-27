from typing import Dict, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import json

# Load environment variables from root directory
load_dotenv(dotenv_path='../../.env')

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7)

class AssistantMemory(BaseModel):
    """Memory structure for the assistant."""
    user_preferences: Dict = Field(default_factory=dict)
    conversation_history: List[Dict] = Field(default_factory=list)
    skills_inventory: Dict = Field(default_factory=dict)
    task_history: List[Dict] = Field(default_factory=list)

class PersonalAssistant:
    """A sophisticated personal assistant with memory and multiple skills."""
    
    def __init__(self, name="Personal Assistant"):
        self.name = name
        self.memory = AssistantMemory()
    
    async def analyze_request(self, request: str) -> Dict:
        """Analyzes user requests and determines the best approach."""
        prompt = f"""Analyze this user request and determine:
        1. Primary need/goal
        2. Required skills
        3. Relevant context from history
        
        Request: {request}
        User History: {json.dumps(self.memory.conversation_history[-3:] if self.memory.conversation_history else [])}
        Preferences: {json.dumps(self.memory.user_preferences)}
        
        Provide analysis in JSON format."""
        
        response = await llm.ainvoke([{"role": "user", "content": prompt}])
        try:
            return json.loads(response.content)
        except:
            return {"error": "Failed to parse analysis", "raw": response.content}
    
    async def generate_response(self, request: str, analysis: Dict) -> str:
        """Generates personalized responses based on analysis."""
        prompt = f"""Create a helpful and personalized response:
        Request: {request}
        Analysis: {json.dumps(analysis)}
        User Preferences: {json.dumps(self.memory.user_preferences)}
        
        Requirements:
        - Be friendly and professional
        - Include specific details from analysis
        - Reference relevant user history when appropriate
        - Provide actionable next steps
        
        Generate the response:"""
        
        response = await llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
    
    async def update_memory(self, request: str, response: str, analysis: Dict):
        """Updates the assistant's memory with new information."""
        # Update conversation history
        self.memory.conversation_history.append({
            'user': request,
            'assistant': response,
            'analysis': analysis
        })
        
        # Update preferences if new information is found
        if 'preferences' in analysis:
            self.memory.user_preferences.update(analysis['preferences'])
        
        # Update skills usage
        if 'skills_used' in analysis:
            for skill in analysis['skills_used']:
                self.memory.skills_inventory[skill] = self.memory.skills_inventory.get(skill, 0) + 1
    
    async def process_request(self, request: str) -> str:
        """Process a user request and return a response."""
        print(f"\nProcessing request: {request}")
        
        # Analyze request
        analysis = await self.analyze_request(request)
        print(f"\nAnalysis: {json.dumps(analysis, indent=2)}")
        
        # Generate response
        response = await self.generate_response(request, analysis)
        print(f"\nGenerated response: {response}")
        
        # Update memory
        await self.update_memory(request, response, analysis)
        
        return response

# Example usage
async def main():
    assistant = PersonalAssistant()
    
    # Example interaction
    request = "I need help developing a workout routine that fits my busy schedule. I prefer morning workouts and have about 30 minutes available."
    
    print("Starting the personal assistant...")
    response = await assistant.process_request(request)
    print("\nFinal response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main()) 