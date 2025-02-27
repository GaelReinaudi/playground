import os
import json
from datetime import datetime
from langgraph_assistant.personal_assistant import EmailAssistant
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_scenarios():
    """Create various test scenarios for the email assistant."""
    return [
        {
            "name": "meeting_request",
            "input": "Help me draft a response to John's meeting request. Make it professional but friendly.",
            "context": {
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
        },
        {
            "name": "follow_up_request",
            "input": "I need to follow up on the project deliverables with the team.",
            "context": {
                "threads": {
                    "thread_2": {
                        "subject": "Project Deliverables Status",
                        "messages": [
                            {
                                "from": "team@example.com",
                                "content": "Here's our progress on the deliverables...",
                                "timestamp": "2024-02-20T14:00:00"
                            }
                        ]
                    }
                },
                "contacts": {
                    "team@example.com": {
                        "name": "Project Team",
                        "role": "Development Team",
                        "previous_interactions": ["status updates", "technical discussions"]
                    }
                },
                "tags": {
                    "thread_2": ["project", "deliverables", "follow-up"]
                }
            }
        },
        {
            "name": "urgent_issue",
            "input": "We have an urgent production issue that needs immediate attention.",
            "context": {
                "threads": {
                    "thread_3": {
                        "subject": "URGENT: Production System Down",
                        "messages": [
                            {
                                "from": "ops@example.com",
                                "content": "The production system is experiencing critical errors.",
                                "timestamp": "2024-02-25T09:00:00"
                            }
                        ]
                    }
                },
                "contacts": {
                    "ops@example.com": {
                        "name": "Operations Team",
                        "role": "System Operations",
                        "previous_interactions": ["system alerts", "maintenance updates"]
                    }
                },
                "tags": {
                    "thread_3": ["urgent", "production", "incident"]
                }
            }
        }
    ]

def run_tests():
    """Run test scenarios and log outputs."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = "data/generated/email_assistant_logs"
    test_dir = os.path.join(base_dir, f"test_run_{timestamp}")
    os.makedirs(test_dir, exist_ok=True)

    # Initialize assistant
    assistant = EmailAssistant()
    scenarios = create_test_scenarios()

    # Process each scenario
    for scenario in scenarios:
        scenario_name = scenario["name"]
        logger.info(f"Processing scenario: {scenario_name}")

        # Create scenario directory
        scenario_dir = os.path.join(test_dir, scenario_name)
        os.makedirs(scenario_dir, exist_ok=True)

        # Process request
        response = assistant.handle_request(scenario["input"], scenario["context"])

        # Log input context
        with open(os.path.join(scenario_dir, "input_context.json"), "w") as f:
            json.dump(scenario["context"], f, indent=2)

        # Log response
        with open(os.path.join(scenario_dir, "response.txt"), "w") as f:
            f.write(response)

        # Log email summary
        for thread_id in scenario["context"]["threads"].keys():
            summary = assistant.get_email_summary(thread_id)
            with open(os.path.join(scenario_dir, f"thread_{thread_id}_summary.json"), "w") as f:
                json.dump(summary, f, indent=2)

        # Log contact history
        for contact_id in scenario["context"]["contacts"].keys():
            history = assistant.get_contact_history(contact_id)
            with open(os.path.join(scenario_dir, f"contact_{contact_id}_history.json"), "w") as f:
                json.dump(history, f, indent=2)

        # Log follow-ups
        follow_ups = assistant.get_pending_follow_ups()
        with open(os.path.join(scenario_dir, "pending_follow_ups.json"), "w") as f:
            json.dump(follow_ups, f, indent=2)

        # Log analytics
        analytics = assistant.get_email_analytics(timeframe="week")
        with open(os.path.join(scenario_dir, "analytics.json"), "w") as f:
            json.dump(analytics, f, indent=2)

        logger.info(f"Completed scenario: {scenario_name}")

    # Create summary report
    with open(os.path.join(test_dir, "test_summary.txt"), "w") as f:
        f.write(f"Email Assistant Test Run Summary\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Number of scenarios: {len(scenarios)}\n\n")
        
        for scenario in scenarios:
            f.write(f"Scenario: {scenario['name']}\n")
            f.write(f"Input: {scenario['input']}\n")
            f.write("-" * 50 + "\n")

    logger.info(f"Test run completed. Results saved in: {test_dir}")
    return test_dir

if __name__ == "__main__":
    output_dir = run_tests()
    print(f"\nTest results saved in: {output_dir}") 