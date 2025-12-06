from bakery import assert_equal
from drafter import *
from dataclasses import dataclass
from drafter.llm import *

set_site_information(
    author="edwinko@udel.edu",
    description="Breaks down large walls of text in terms and conditions into easy to understand summaries " \
    "highlighting privacy concerns and red flags. Next steps: improve consistency of API calls and add the " \
    "option to search for website terms and conditions directly from the app.",
    sources="Google Gemini API", 
    planning= "",
    links=["https://github.com/edwinko-alt/Fine-Print-Buster"]
)

set_gemini_server("https://drafter-gemini-proxy.edwinko.workers.dev/")


hide_debug_information()
set_website_title("Fine Print Buster")
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
        f"Terms and Conditions Analyzer",
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
        Button("Send", send_message), # type: ignore
        ]) # type: ignore

    return Page(state, content)

@route
def send_message(state: State, user_message: str) -> Page:
    """Send a message to the LLM and get a response."""
    if not user_message.strip():
        return show_chat(state)
    
    clear_conversation(state)
    # Add user message to conversation
    initialize_prompt = "The user will send in a terms and conditions document. Analyze it for privacy concerns and red flags. Output it" \
    "in the format: Privacy Rating (1-10): X -> new line -> Red Flags: [list of red flags]. -> new line -> Scenario: <worst case scenario>. Also," \
    "can you analyze the text and return the response in HTML format? " \
    "Additionally, please try to be funny and engaging in your analysis, but please get to the point quickly. People want to read" \
    "short and to the point bullet points. Try to include images if possible"

    user_msg = LLMMessage("user", initialize_prompt + "\n" + user_message)
    state.conversation.append(user_msg)

    result = call_gemini(state.conversation, max_tokens=7000)

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