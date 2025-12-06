from bakery import assert_equal
from drafter import *
from dataclasses import dataclass
from drafter.llm import *

#import requests

set_site_information(
    author="your_email@udel.edu",
    description="A brief description of what your website does",
    sources="List any help resources or sources you used",
    planning="your_planning_document.pdf",
    links=["https://github.com/your-username/your-repo"]
)

set_gemini_server("https://drafter-gemini-proxy.edwinko.workers.dev/")


hide_debug_information()
set_website_title("Fine Print Pirate")
set_website_framed(False)




@dataclass
class State:
    """
    The state of our chatbot application.

    :param conversation: List of messages in the conversation
    :type conversation: List[LLMMessage]
    """
    conversation: list[LLMMessage]


@route
def index(state: State) -> Page:
    """
    Main page of the chatbot application.
    Shows API key setup if not configured, otherwise shows the chat interface.
    """
    return show_chat(state)


def show_chat(state: State) -> Page:
    """Display the chat interface with conversation history."""
    content = [
        f"Chatbot using Gemini",
        "---"
    ]

    # Show conversation history
    if state.conversation:
        for msg in state.conversation:
            if msg.role == "user":
                content.append(f"You: {msg.content}")
            elif msg.role == "assistant":
                content.append(f"Bot: {msg.content}")
        content.append("---")

    # Input for new message
    content.extend([
        "Your message:",
        TextArea("user_message", "", rows=3, cols=50),
        LineBreak(),
        Button("Send", send_message),
        Button("Clear Conversation", clear_conversation),
    ])

    return Page(state, content)

@route
def send_message(state: State, user_message: str) -> Page:
    """Send a message to the LLM and get a response."""
    if not user_message.strip():
        return show_chat(state)

    prompt = "You are a Gen Z teen who is a rockstar at roasting company terms and conditions. Respond to the users message in a quirky, relatable way " + user_message
    # Add user message to conversation
    user_msg = LLMMessage("user", prompt)
    state.conversation.append(user_msg)

    result = call_gemini(state.conversation)

    # Handle the result
    if isinstance(result, LLMResponse):
        # Success! Add the response to conversation
        assistant_msg = LLMMessage("assistant", result.content)
        state.conversation.append(assistant_msg)
    else:
        # Error occurred
        error_msg = LLMMessage("assistant", f"Error: {result.message}")
        state.conversation.append(error_msg)
        
    return show_chat(state)

@route
def clear_conversation(state: State) -> Page:
    """Clear the conversation history."""
    state.conversation = []
    return show_chat(state)

set_website_style("simple")
start_server(State([]))