import sys
import warnings

# FIX 1: Force UTF-8 encoding so the terminal never crashes on LLM characters
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
warnings.filterwarnings("ignore")

import os
import time # Imported for rate-limiting
from typing import TypedDict
from pydantic import BaseModel, Field
from dotenv import load_dotenv

import wikipedia
wikipedia.set_user_agent("MultiAgentApp/1.0 (student-project)")

from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph import StateGraph, START, END

load_dotenv()
if not os.getenv("OPENROUTER_API_KEY"):
    raise ValueError("OPENROUTER_API_KEY is missing.")

llm = ChatOpenAI(
    model="openai/gpt-oss-20b:free", 
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.4,
    max_retries=1,      # Don't let it silently retry forever
    timeout=45.0        # Force a failure if OpenRouter hangs for 45 seconds
)

class AgentState(TypedDict):
    topic: str
    research_notes: str
    draft: str
    editor_feedback: str
    approved: bool
    final_article: str
    iteration: int

def researcher_node(state: AgentState):
    print("\n[Researcher] Searching Wikipedia for factual information...")
    api_wrapper = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=2000)
    search_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
    
    query = state['topic']
    raw_info = search_tool.invoke(query)
    return {"research_notes": raw_info}

def writer_node(state: AgentState):
    iteration = state.get("iteration", 0) + 1
    print(f"\n[Writer] Drafting article (Attempt {iteration})...")
    
    prompt = f"""You are an expert technical writer. Write a BRIEF, 3-paragraph summary on the topic: {state['topic']}
    Use these raw research notes to ground your facts: {state.get('research_notes', '')}
    Keep it concise. Do not write a massive essay.
    """
    
    if state.get("editor_feedback"):
        prompt += f"\n\nCRITICAL - Revise your previous draft using this editor feedback: {state['editor_feedback']}"
        prompt += f"\n\nHere is your Previous Draft to improve upon:\n{state['draft']}"
        
    response = llm.invoke(prompt)
    return {"draft": response.content, "iteration": iteration}

def editor_node(state: AgentState):
    print("\n[Editor] Reviewing the draft...")
    
    prompt = f"""You are a strict senior editor. Review this draft about '{state['topic']}'.
    Ensure it is engaging, structurally sound, and factually based.
    
    You MUST respond using EXACTLY this format:
    APPROVED: True (or False)
    FEEDBACK: Write your detailed feedback here.
    
    Draft to review:
    {state['draft']}
    """
    
    response_text = llm.invoke(prompt).content
    
    is_approved = False
    if "APPROVED: True" in response_text or "APPROVED: TRUE" in response_text:
        is_approved = True
        
    feedback_text = "No specific feedback provided."
    if "FEEDBACK:" in response_text:
        feedback_text = response_text.split("FEEDBACK:")[1].strip()
        
    print(f"[Editor] Approved? {is_approved}")
    if not is_approved:
        print(f"[Editor] Feedback: {feedback_text}")
        
    return {
        "approved": is_approved, 
        "editor_feedback": feedback_text,
        "final_article": state['draft']
    }

def route_approval(state: AgentState):
    if state["approved"] or state["iteration"] >= 3:
        # FIX 2: Return the actual END object, not a string
        return END
    
    # FIX 3: Pause to prevent free-tier API blocking
    print("\n[Supervisor] Feedback sent. Pausing to respect API rate limits...")
    time.sleep(3)
    return "writer_node"

workflow = StateGraph(AgentState)

workflow.add_node("researcher_node", researcher_node)
workflow.add_node("writer_node", writer_node)
workflow.add_node("editor_node", editor_node)

workflow.add_edge(START, "researcher_node")
workflow.add_edge("researcher_node", "writer_node")
workflow.add_edge("writer_node", "editor_node")

# FIX 4: Explicitly map the routing targets
workflow.add_conditional_edges(
    "editor_node", 
    route_approval,
    {"writer_node": "writer_node", END: END}
)

app = workflow.compile()

if __name__ == "__main__":
    # Grab the topic from the command line argument (passed by Node.js)
    # If nothing is passed, fallback to a default
    user_topic = sys.argv[1] if len(sys.argv) > 1 else "Artificial Intelligence"
    
    initial_state = {
        "topic": user_topic, # Inject dynamic topic here
        "research_notes": "",
        "draft": "",
        "editor_feedback": "",
        "approved": False,
        "final_article": "",
        "iteration": 0
    }
    
    print(f"\n[System] Initializing pipeline for topic: {user_topic}")
    final_state = app.invoke(initial_state)
    
    print("\n" + "="*60)
    print(f"🎯 FINAL PUBLISHED ARTICLE (After {final_state['iteration']} iterations):")
    print("="*60)
    print(final_state["final_article"])