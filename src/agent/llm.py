from langchain_groq import ChatGroq
from src.core.config import settings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

llm = ChatGroq(
    temperature=0,
    groq_api_key=settings.GROQ_API_KEY,
    model_name="llama-3.1-8b-instant"
)

SYSTEM_TEMPLATE = """You are an expert software engineer and AI assistant for the RepoSage platform.

Context from the repository:
{retrieved_chunks}

Instructions:
1. Technical questions: Provide precise answers, referencing files and functions.
2. Conceptual/Project questions (e.g., architecture, purpose, accuracy, scaling): Use the context to deduce the answer or provide logical insights based on general software engineering principles and the conversational history.
3. Be conversational and helpful. Do not mention your limitations if you can infer the answer from the general system context.
4. Do not hallucinate exact file names if not found. Only use those provided.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_TEMPLATE),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_query}")
])

def generate_answer(query: str, context: str, chat_history: list = None) -> str:
    langchain_history = []
    if chat_history:
        for msg in chat_history:
            if msg["role"] == "user":
                langchain_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_history.append(AIMessage(content=msg["content"]))

    chain = prompt | llm
    res = chain.invoke({
        "user_query": query, 
        "retrieved_chunks": context,
        "chat_history": langchain_history
    })
    return res.content

EVAL_PROMPT = """You are a grader assessing whether an answer is correct and useful for a user question based on the retrieved context.
Output only "yes" if the answer is accurate and resolves the question, or "no" if it hallucinated or failed to answer.

Context:
{context}

Question:
{user_query}

Answer:
{answer}
"""
eval_prompt = PromptTemplate(template=EVAL_PROMPT, input_variables=["context", "user_query", "answer"])

def evaluate_answer(query: str, context: str, answer: str) -> str:
    chain = eval_prompt | llm
    res = chain.invoke({"context": context, "user_query": query, "answer": answer})
    return res.content.strip().lower()

REWRITE_PROMPT = """You are a question re-writer assistant. The user's previous question failed to yield a useful answer from the vector database.
Rewrite the question to be more specific or use different semantic keywords so we can search the codebase again effectively.
Output ONLY the rewritten question and nothing else.

Original Question: {user_query}
"""
rewrite_prompt = PromptTemplate(template=REWRITE_PROMPT, input_variables=["user_query"])

def rewrite_question(query: str) -> str:
    chain = rewrite_prompt | llm
    res = chain.invoke({"user_query": query})
    return res.content.strip()
