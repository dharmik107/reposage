from langgraph.graph import StateGraph, START, END
from src.agent.nodes import GraphState, embed_query_node, retrieve_node, context_builder_node, generator_node, rewrite_node
from src.agent.llm import evaluate_answer

def evaluate_condition(state: GraphState) -> str:
    # If we already retried too many times, just return whatever we have
    if state.get("retry_count", 0) >= 2:
        return "useful"
        
    score = evaluate_answer(state["question"], state["context_str"], state["answer"])
    if "yes" in score:
        return "useful"
    else:
        return "not_useful"

def build_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("embed", embed_query_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("context", context_builder_node)
    workflow.add_node("generate", generator_node)
    workflow.add_node("rewrite", rewrite_node)
    
    workflow.add_edge(START, "embed")
    workflow.add_edge("embed", "retrieve")
    workflow.add_edge("retrieve", "context")
    workflow.add_edge("context", "generate")
    
    workflow.add_conditional_edges(
        "generate",
        evaluate_condition,
        {
            "useful": END,
            "not_useful": "rewrite"
        }
    )
    
    workflow.add_edge("rewrite", "embed")
    
    return workflow.compile()

graph = build_graph()

def process_query(repo_id: str, question: str, chat_history: list = None) -> dict:
    state = {
        "question": question,
        "repo_id": repo_id,
        "query_embedding": [],
        "retrieved_docs": [],
        "context_str": "",
        "answer": "",
        "retry_count": 0,
        "chat_history": chat_history or []
    }
    
    result = graph.invoke(state)
    
    return {
        "answer": result["answer"],
        "references": [
            {
                "file": doc["file"],
                "function": doc["function"],
                "lines": doc["lines"]
            } for doc in result["retrieved_docs"]
        ]
    }
