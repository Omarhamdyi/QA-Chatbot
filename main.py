import os 
from dotenv import load_dotenv
load_dotenv()


from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langsmith import traceable,Client
from typing import List
from pprint import pprint


#langsmith configuration
if os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ.setdefault("LANGSMITH_PROJECT", "QA-Chatbot")
    # print(f"{os.getenv("LANGSMITH_PROJECT")}")



#Schema Definition
class QAResponse(BaseModel):
    answer:str = Field(description= "The answer to the user's question.")
    confidence:str = Field(description = "Confidence level: high, medium, or low")
    reasoning: str = Field(description= "The reasoning behind the answer provided.")
    follow_up_questions: List[str] =Field(description ="A list of follow-up questions related to the topic.",default_factory =list )



class QAChatbot:
    def __init__(self, model_name : str = "command-a-03-2025" , temperature: float = 0.3, max_tokens :int = 1500):
        
        self.base_model = init_chat_model(model = model_name,temperature = temperature , max_tokens = max_tokens)
        self.model = self.base_model.with_structured_output(QAResponse)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system" , """You are a knowledgeable Q&A assistant.

                            Your guidelines:
                            - Answer questions accurately and concisely
                            - Be honest about uncertainty - set confidence to 'low' if unsure
                            - Provide clear reasoning for your answers
                            - Suggest relevant follow-up questions
                            - Indicate if external sources would help

                            Always respond with accurate, helpful information."""
            ),
            ("human" , "{question}")
        ])
        self.chain = self.prompt | self.model
        self.stream_chain = self.prompt | self.base_model

    def _error_response(self, error: Exception) -> QAResponse:
        return QAResponse(
            answer="I'm sorry, I couldn't process your question at this time.",
            confidence="low",
            reasoning=str(error),
            follow_up_questions=["Could you please try again later?"],
            sources_needed=True,
        )

    @traceable(name="ask_single_stream", run_type="chain")
    def ask_single_stream(self, question: str):
        try:
            for chunk in self.chain.stream({"question": question}):
                yield chunk
        except Exception as e:
            yield self._error_response(e)

    @traceable(name="ask_single_stream_text", run_type="chain")
    def ask_single_stream_text(self, question: str):
        try:
            for chunk in self.stream_chain.stream({"question": question}):
                text = getattr(chunk, "content", "")
                if text:
                    yield text
        except Exception as e:
            yield self._error_response(e).answer
        
        
    @traceable(name="ask_batch", run_type="chain")
    def ask_batch(self, questions: list[str]) -> list[QAResponse]:
        try:
            payloads = [{"question": q} for q in questions]
            return self.chain.batch(payloads)
        except Exception as e:
            return [self._error_response(e)]

    def ask(self, question_or_questions: str | list[str]):
        if isinstance(question_or_questions, str):
            return self.ask_single_stream(question_or_questions)
        if isinstance(question_or_questions, list):
            if len(question_or_questions) == 1:
                return self.ask_single_stream(question_or_questions[0])
            return self.ask_batch(question_or_questions)
        raise TypeError("Input must be a string or a list of strings.")


        


def demo():
    bot = QAChatbot()
    for chunk in bot.ask_single_stream("What is AI?"):
        if isinstance(chunk, QAResponse):
            print(chunk.answer, end="", flush=True)
        elif hasattr(chunk, "answer"):
            print(chunk.answer, end="", flush=True)
        elif hasattr(chunk, "content"):
            print(chunk.content, end="", flush=True)
        else:
            print(str(chunk), end="", flush=True)

if __name__=="__main__":
    demo()
