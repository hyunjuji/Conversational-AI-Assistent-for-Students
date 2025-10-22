import gradio as gr
from src.main import run_full_turn, triage_agent

def _content(m):
    return m["content"] if isinstance(m, dict) else m.content

def _role(m):
    return m["role"] if isinstance(m, dict) else m.role

def chat_fn(user_msg, history, state):
    state = state or {"agent": triage_agent, "messages": []}
    state["messages"].append({"role": "user", "content": user_msg})

    resp = run_full_turn(state["agent"], state["messages"])
    state["agent"] = resp.agent
    state["messages"].extend(resp.messages)

    assistant_reply = "".join(
        _content(m) for m in resp.messages if _role(m) == "assistant"
    )
    history.append((user_msg, assistant_reply))
    return history, state

demo = gr.ChatInterface(fn=chat_fn, state=gr.State()).queue()
demo.launch()