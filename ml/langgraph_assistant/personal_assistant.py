from typing import Dict, TypedDict, Annotated, Sequence, List
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import operator
import json
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from root directory
load_dotenv(dotenv_path='../../.env')

# Define state schema
class EmailState(TypedDict):
    messages: List[Dict]
    context: Dict
    current_task: str
    memory: Dict
    email_threads: Dict[str, Dict]
    contacts: Dict[str, Dict]
    drafts: Dict[str, Dict]
    tags: Dict[str, List[str]]
    follow_ups: Dict[str, Dict]
    priorities: Dict[str, str]
    response_templates: Dict[str, str]
    email_stats: Dict[str, Dict]

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7)

# Define agent nodes
def context_analyzer(state: EmailState) -> EmailState:
    """Analyzes email context and maintains conversation history."""
    messages = state['messages']
    context = state['context']
    email_threads = state['email_threads']
    contacts = state['contacts']
    
    prompt = f"""As an email assistant, analyze the conversation and email context:
    Current context: {json.dumps(context)}
    Email threads: {json.dumps(email_threads)}
    Contact history: {json.dumps(contacts)}
    Previous messages: {messages[-3:] if len(messages) > 3 else messages}
    
    Update the context with:
    1. Key topics and themes
    2. Important deadlines or follow-ups
    3. Relationship context with contacts
    4. Action items and priorities
    5. Related threads and conversations
    6. Suggested response templates
    7. Follow-up recommendations
    Return a JSON object with updates."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        context_updates = json.loads(response.content)
        if isinstance(context_updates, dict):
            state['context'].update(context_updates)
            
            # Update follow-ups if detected
            if 'follow_ups' in context_updates:
                state['follow_ups'].update(context_updates['follow_ups'])
            
            # Update priorities if detected
            if 'priorities' in context_updates:
                state['priorities'].update(context_updates['priorities'])
            
            # Update email stats
            thread_id = context_updates.get('thread_id')
            if thread_id:
                if thread_id not in state['email_stats']:
                    state['email_stats'][thread_id] = {
                        'interaction_count': 0,
                        'last_interaction': datetime.now().isoformat(),
                        'topics': set(),
                        'sentiment_history': []
                    }
                state['email_stats'][thread_id]['interaction_count'] += 1
                state['email_stats'][thread_id]['last_interaction'] = datetime.now().isoformat()
                
                if 'topics' in context_updates:
                    state['email_stats'][thread_id]['topics'].update(context_updates['topics'])
                if 'sentiment' in context_updates:
                    state['email_stats'][thread_id]['sentiment_history'].append({
                        'timestamp': datetime.now().isoformat(),
                        'sentiment': context_updates['sentiment']
                    })
    except:
        logger.error("Failed to parse context updates")
    
    return state

def email_router(state: EmailState) -> EmailState:
    """Routes email-related requests to appropriate handlers."""
    messages = state['messages']
    last_message = messages[-1]
    
    prompt = f"""Analyze this email-related request and determine the primary task needed:
    Request: {last_message}
    
    Available tasks: ['compose_email', 'analyze_email', 'summarize_email', 'generate_response']
    Return only one task name."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    task = str(response.content).strip().lower()
    
    # Map old task names to new ones if needed
    task_mapping = {
        'compose': 'compose_email',
        'analyze': 'analyze_email',
        'summarize': 'summarize_email',
        'respond': 'generate_response'
    }
    
    state['current_task'] = task_mapping.get(task, task)
    return state

def email_composer(state: EmailState) -> EmailState:
    """Handles email composition and drafting."""
    messages = state['messages']
    context = state['context']
    contacts = state['contacts']
    
    prompt = f"""As an email composer, help draft or modify an email:
    Request: {messages[-1]}
    Context: {json.dumps(context)}
    Contact History: {json.dumps(contacts)}
    
    Consider:
    1. Appropriate tone and style
    2. Previous interactions
    3. Key points to address
    4. Clear call-to-action
    
    Draft the email content."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    if 'drafts' not in state:
        state['drafts'] = {}
    
    draft_id = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    state['drafts'][draft_id] = {
        'content': response.content,
        'context': context,
        'timestamp': datetime.now().isoformat()
    }
    
    return state

def email_analyzer(state: EmailState) -> EmailState:
    """Analyzes email content and provides insights."""
    messages = state['messages']
    context = state['context']
    email_threads = state['email_threads']
    contacts = state['contacts']
    email_stats = state['email_stats']
    
    prompt = f"""Analyze this email thread and provide comprehensive insights:
    Request: {messages[-1]}
    Context: {json.dumps(context)}
    Email Thread: {json.dumps(email_threads)}
    Contact History: {json.dumps(contacts)}
    Previous Interactions: {json.dumps(email_stats)}
    
    Provide detailed analysis including:
    1. Key points and main topics
    2. Sentiment analysis and tone
    3. Action items and deadlines
    4. Required follow-ups and timeline
    5. Priority level (urgent/high/medium/low)
    6. Related threads or conversations
    7. Contact relationship insights
    8. Suggested response strategy
    9. Recommended response templates
    10. Time sensitivity assessment
    
    Return analysis in JSON format with clear categorization."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        analysis = json.loads(response.content)
        if 'memory' not in state:
            state['memory'] = {}
        state['memory']['analysis'] = analysis
        
        # Update email stats and tracking
        if 'thread_id' in analysis:
            thread_id = analysis['thread_id']
            if thread_id not in state['email_stats']:
                state['email_stats'][thread_id] = {
                    'interaction_count': 0,
                    'last_interaction': datetime.now().isoformat(),
                    'topics': [],
                    'sentiment_history': [],
                    'priority_history': [],
                    'action_items': [],
                    'deadlines': []
                }
            
            # Update various tracking metrics
            if 'topics' in analysis:
                topics = list(analysis['topics']) if isinstance(analysis['topics'], set) else analysis['topics']
                current_topics = state['email_stats'][thread_id]['topics']
                state['email_stats'][thread_id]['topics'] = list(set(current_topics + topics))
            
            if 'sentiment' in analysis:
                state['email_stats'][thread_id]['sentiment_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'sentiment': analysis['sentiment']
                })
            if 'priority' in analysis:
                state['email_stats'][thread_id]['priority_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'priority': analysis['priority']
                })
            if 'action_items' in analysis:
                state['email_stats'][thread_id]['action_items'].extend(analysis['action_items'])
            if 'deadlines' in analysis:
                state['email_stats'][thread_id]['deadlines'].extend(analysis['deadlines'])
            
            # Update follow-ups
            if 'follow_ups' in analysis:
                state['follow_ups'][thread_id] = {
                    'items': analysis['follow_ups'],
                    'created_at': datetime.now().isoformat(),
                    'status': 'pending'
                }
            
            # Update priorities
            if 'priority' in analysis:
                state['priorities'][thread_id] = analysis['priority']
            
            # Update response templates
            if 'suggested_templates' in analysis:
                for template_name, template_content in analysis['suggested_templates'].items():
                    state['response_templates'][template_name] = template_content
    except:
        logger.error("Failed to parse email analysis")
    
    return state

def email_summarizer(state: EmailState) -> EmailState:
    """Summarizes email threads and conversations."""
    messages = state['messages']
    email_threads = state['email_threads']
    
    prompt = f"""Summarize this email thread concisely:
    Thread: {json.dumps(email_threads)}
    Request: {messages[-1]}
    
    Provide:
    1. Main topics
    2. Key decisions
    3. Action items
    4. Important dates
    5. Next steps"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    if 'memory' not in state:
        state['memory'] = {}
    state['memory']['summary'] = response.content
    return state

def response_generator(state: EmailState) -> EmailState:
    """Generates appropriate email responses with context awareness."""
    context = state['context']
    memory = state['memory']
    drafts = state['drafts']
    email_stats = state['email_stats']
    follow_ups = state['follow_ups']
    priorities = state['priorities']
    response_templates = state['response_templates']
    
    analysis = memory.get('analysis', {})
    thread_id = analysis.get('thread_id')
    
    prompt = f"""Generate a contextually aware email response based on:
    Context: {json.dumps(context)}
    Analysis: {json.dumps(analysis)}
    Email Stats: {json.dumps(email_stats.get(thread_id, {}))}
    Follow-ups: {json.dumps(follow_ups.get(thread_id, {}))}
    Priority: {json.dumps(priorities.get(thread_id, 'medium'))}
    Available Templates: {json.dumps(response_templates)}
    
    Requirements:
    1. Professional and appropriate tone matching previous interactions
    2. Address all action items and questions
    3. Include relevant context from previous conversations
    4. Clear next steps and expectations
    5. Appropriate follow-up timeline
    6. Priority-appropriate response timing
    7. Maintain relationship context
    8. Reference related threads if relevant
    
    Generate a complete response with:
    - Subject line (if needed)
    - Greeting appropriate to relationship
    - Main content
    - Clear action items or next steps
    - Professional closing"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    new_messages = list(state['messages'])
    new_messages.append({"role": "assistant", "content": response.content})
    state['messages'] = new_messages
    
    # Save draft
    draft_id = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    state['drafts'][draft_id] = {
        'content': response.content,
        'context': context,
        'analysis': analysis,
        'thread_id': thread_id,
        'timestamp': datetime.now().isoformat(),
        'status': 'draft'
    }
    
    return state

def should_continue(state: EmailState) -> str:
    """Determines which node to route to based on the current task."""
    current_task = state.get('current_task', '')
    if current_task == 'compose':
        return 'compose_email'
    elif current_task == 'analyze':
        return 'analyze_email'
    elif current_task == 'summarize':
        return 'summarize_email'
    else:
        return 'generate_response'

# Create the graph
def create_graph():
    workflow = StateGraph(EmailState)
    
    # Add nodes
    workflow.add_node("context_analysis", context_analyzer)
    workflow.add_node("route_request", email_router)
    workflow.add_node("compose_email", email_composer)
    workflow.add_node("analyze_email", email_analyzer)
    workflow.add_node("summarize_email", email_summarizer)
    workflow.add_node("generate_response", response_generator)
    
    # Add edges
    workflow.add_edge("context_analysis", "route_request")
    workflow.add_conditional_edges(
        "route_request",
        should_continue,
        {
            "compose_email": "compose_email",
            "analyze_email": "analyze_email",
            "summarize_email": "summarize_email",
            "generate_response": "generate_response"
        }
    )
    workflow.add_edge("compose_email", "generate_response")
    workflow.add_edge("analyze_email", "generate_response")
    workflow.add_edge("summarize_email", "generate_response")
    
    # Set entry point
    workflow.set_entry_point("context_analysis")
    
    # Set exit point
    workflow.set_finish_point("generate_response")
    
    return workflow.compile()

class EmailAssistant:
    def __init__(self):
        self.graph = create_graph()
        self.context = {
            "preferences": {},
            "history": [],
            "email_settings": {
                "signature": "",
                "default_tone": "professional",
                "priority_rules": {},
                "follow_up_preferences": {
                    "default_timeline": "3 days",
                    "urgent_timeline": "24 hours",
                    "reminder_frequency": "daily"
                }
            }
        }
        self.memory = {}
        self.email_threads = {}
        self.contacts = {}
        self.drafts = {}
        self.tags = {}
        self.follow_ups = {}
        self.priorities = {}
        self.response_templates = {}
        self.email_stats = {}
    
    def handle_request(self, user_input: str, email_context: Dict = None) -> str:
        # Prepare the initial state
        state = {
            "messages": [{"role": "user", "content": user_input}],
            "context": self.context,
            "current_task": "",
            "memory": self.memory,
            "email_threads": self.email_threads,
            "contacts": self.contacts,
            "drafts": self.drafts,
            "tags": self.tags,
            "follow_ups": self.follow_ups,
            "priorities": self.priorities,
            "response_templates": self.response_templates,
            "email_stats": self.email_stats
        }
        
        # Update context with email-specific information
        if email_context:
            state["email_threads"].update(email_context.get("threads", {}))
            state["contacts"].update(email_context.get("contacts", {}))
            state["tags"].update(email_context.get("tags", {}))
        
        # Run the graph
        final_state = self.graph.invoke(state)
        
        # Update internal state
        self.context = final_state['context']
        self.memory = final_state['memory']
        self.email_threads = final_state['email_threads']
        self.contacts = final_state['contacts']
        self.drafts = final_state['drafts']
        self.tags = final_state['tags']
        self.follow_ups = final_state['follow_ups']
        self.priorities = final_state['priorities']
        self.response_templates = final_state['response_templates']
        self.email_stats = final_state['email_stats']
        
        # Return the last assistant message
        return final_state['messages'][-1]['content']

    def get_pending_follow_ups(self) -> List[Dict]:
        """Get all pending follow-ups sorted by priority and deadline."""
        pending = []
        for thread_id, follow_up in self.follow_ups.items():
            if follow_up['status'] == 'pending':
                priority = self.priorities.get(thread_id, 'medium')
                pending.append({
                    'thread_id': thread_id,
                    'items': follow_up['items'],
                    'created_at': follow_up['created_at'],
                    'priority': priority
                })
        
        # Sort by priority and creation date
        priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        return sorted(pending, key=lambda x: (priority_order[x['priority']], x['created_at']))

    def get_email_summary(self, thread_id: str) -> Dict:
        """Get a comprehensive summary of an email thread."""
        if thread_id not in self.email_threads:
            return {"error": "Thread not found"}
        
        return {
            "thread": self.email_threads[thread_id],
            "stats": self.email_stats.get(thread_id, {}),
            "follow_ups": self.follow_ups.get(thread_id, {}),
            "priority": self.priorities.get(thread_id, 'medium'),
            "drafts": {k: v for k, v in self.drafts.items() if v.get('thread_id') == thread_id}
        }

    def get_contact_history(self, contact_id: str) -> Dict:
        """Get interaction history with a specific contact."""
        if contact_id not in self.contacts:
            return {"error": "Contact not found"}
        
        contact_threads = []
        for thread_id, thread in self.email_threads.items():
            if contact_id in thread.get('participants', []):
                contact_threads.append({
                    "thread_id": thread_id,
                    "stats": self.email_stats.get(thread_id, {}),
                    "last_interaction": thread.get('last_interaction'),
                    "priority": self.priorities.get(thread_id, 'medium')
                })
        
        return {
            "contact": self.contacts[contact_id],
            "threads": contact_threads,
            "interaction_summary": {
                "total_threads": len(contact_threads),
                "pending_follow_ups": sum(1 for t in contact_threads if thread_id in self.follow_ups and self.follow_ups[thread_id]['status'] == 'pending'),
                "priority_distribution": self._get_priority_distribution(contact_threads)
            }
        }

    def _get_priority_distribution(self, threads: List[Dict]) -> Dict[str, int]:
        """Helper function to get priority distribution."""
        distribution = {'urgent': 0, 'high': 0, 'medium': 0, 'low': 0}
        for thread in threads:
            priority = thread.get('priority', 'medium')
            distribution[priority] += 1
        return distribution

    def mark_follow_up_complete(self, thread_id: str, follow_up_id: str = None):
        """Mark a follow-up as complete."""
        if thread_id in self.follow_ups:
            if follow_up_id:
                # Mark specific follow-up item as complete
                for item in self.follow_ups[thread_id]['items']:
                    if item.get('id') == follow_up_id:
                        item['status'] = 'completed'
                        item['completed_at'] = datetime.now().isoformat()
            else:
                # Mark all follow-ups for thread as complete
                self.follow_ups[thread_id]['status'] = 'completed'
                self.follow_ups[thread_id]['completed_at'] = datetime.now().isoformat()

    def update_email_priority(self, thread_id: str, priority: str):
        """Update the priority of an email thread."""
        if priority not in ['urgent', 'high', 'medium', 'low']:
            raise ValueError("Invalid priority level")
        
        self.priorities[thread_id] = priority
        if thread_id in self.email_stats:
            self.email_stats[thread_id]['priority_history'].append({
                'timestamp': datetime.now().isoformat(),
                'priority': priority
            })

    def get_email_analytics(self, timeframe: str = 'week') -> Dict:
        """Get analytics about email interactions."""
        now = datetime.now()
        
        if timeframe == 'day':
            delta = timedelta(days=1)
        elif timeframe == 'week':
            delta = timedelta(weeks=1)
        elif timeframe == 'month':
            delta = timedelta(days=30)
        else:
            raise ValueError("Invalid timeframe")
        
        cutoff = now - delta
        
        analytics = {
            'total_threads': 0,
            'priority_distribution': {'urgent': 0, 'high': 0, 'medium': 0, 'low': 0},
            'response_times': [],
            'pending_follow_ups': 0,
            'completed_follow_ups': 0,
            'topics': [],
            'sentiment_summary': []
        }
        
        all_topics = set()
        
        for thread_id, stats in self.email_stats.items():
            last_interaction = datetime.fromisoformat(stats['last_interaction'])
            if last_interaction >= cutoff:
                analytics['total_threads'] += 1
                analytics['priority_distribution'][self.priorities.get(thread_id, 'medium')] += 1
                all_topics.update(stats.get('topics', []))
                
                if thread_id in self.follow_ups:
                    if self.follow_ups[thread_id]['status'] == 'pending':
                        analytics['pending_follow_ups'] += 1
                    else:
                        analytics['completed_follow_ups'] += 1
                
                # Add sentiment data
                for sentiment in stats.get('sentiment_history', []):
                    sentiment_date = datetime.fromisoformat(sentiment['timestamp'])
                    if sentiment_date >= cutoff:
                        analytics['sentiment_summary'].append(sentiment['sentiment'])
        
        # Convert the topics set to a sorted list
        analytics['topics'] = sorted(list(all_topics))
        
        return analytics

# Example usage
if __name__ == "__main__":
    assistant = EmailAssistant()
    
    # Example interaction
    email_context = {
        "threads": {
            "thread_1": {
                "subject": "Project Update Meeting",
                "messages": [
                    {
                        "from": "john@example.com",
                        "content": "Can we schedule a project update meeting for next week?",
                        "timestamp": "2024-02-25T10:00:00"
                    }
                ]
            }
        },
        "contacts": {
            "john@example.com": {
                "name": "John Smith",
                "role": "Project Manager",
                "previous_interactions": ["meeting requests", "status updates"]
            }
        },
        "tags": {
            "thread_1": ["project", "meeting", "high-priority"]
        }
    }
    
    user_input = "Help me draft a response to John's meeting request. Make it professional but friendly."
    logger.info(f"Processing request: {user_input}")
    
    response = assistant.handle_request(user_input, email_context)
    logger.info("Request processed successfully")
    print(f"\nAssistant's response: {response}") 