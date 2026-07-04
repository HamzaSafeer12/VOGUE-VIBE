from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from dotenv import load_dotenv
import os
from openai import OpenAI, OpenAIError
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
# from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain.agents.middleware import ToolCallLimitMiddleware, before_model, after_model,AgentState
# Create your views here.
class FirstCallAI(APIView):
    load_dotenv()
    # API key read
    
    # OpenAI client

    def post(self, request):
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        user_input = request.data.get("message")
        if not user_input:
            return Response({'error':'no question?'}, status=400)
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_input}]
            )
            ai_reply = response['choices'][0]['message']['content']
            return({"reply":ai_reply})

        except Exception as e:
            return Response({"error":str(e)},status=500)

class LangChainClass(APIView):

     def post(self, request):
         user_input = request.data.get("message")
         if not user_input:
             return Response({"error":"not found"},status=400)
         
         try:
             llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.7)
             response = llm.invoke(user_input)
             return Response({"reply":response.content})
         except Exception as e:
             return Response({"Error":str(e)})

class Promptchainsmodel(APIView):
    def post(self, request):
        print("Welcome to prompt chains")
        topic = request.data.get("topic")
        if not topic:
            return Response({"error":"not found"},status=400)
        
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature = 0.7)
            prompt = PromptTemplate(input_varaiables=["topic"], template="Explain {topic} for biggeners")
            chain = prompt | llm
            response = chain.invoke({"topic": topic})
            return Response({"reply":response})
        except(Exception) as e:
            return Response({"Error":str(e)})
        

class chainpromptmodel_OutPut_Parser(APIView):
    # def post(self, request):
    #     topic = request.data.get("topic")

    #     if not topic:
    #         return Response({"error": "topic not found"}, status=400)

    #     try:
    #         llm = ChatOpenAI(
    #             model="gpt-4.1-mini",
    #             temperature=0.7
    #         )

    #         response_schemas = [
    #             ResponseSchema(
    #                 name="definition",
    #                 description="Simple definition for a beginner"
    #             ),
    #             ResponseSchema(
    #                 name="example",
    #                 description="Simple real world example"
    #             ),
    #             ResponseSchema(
    #                 name="use_cases",
    #                 description="List of common use cases"
    #             )
    #         ]

    #         output_parser = StructuredOutputParser.from_response_schemas(
    #             response_schemas
    #         )

    #         format_instructions = output_parser.get_format_instructions()

    #         prompt = PromptTemplate(
    #             input_variables=["topic"],
    #             template="""
    #         Explain the concept of {topic} for a beginner.

    #         {format_instructions}
    #         """,
    #             partial_variables={
    #                 "format_instructions": format_instructions
    #             }
    #         )

    #         chain = prompt | llm
    #         response = chain.invoke({"topic": topic})

    #         parsed_output = output_parser.parse(response.content)

    #         return Response(parsed_output)

    #     except Exception as e:
    #         return Response({"error": str(e)}, status=500)
        

    def post(self, request):
        topic = request.data.get("topic")

        if not topic:
            return Response({"error": "topic not found"}, status=400)

        try:
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7
            )

            parser = JsonOutputParser()
            format_instructions = parser.get_format_instructions()

            prompt = PromptTemplate(
                input_variables=["topic"],
                template="""
    Explain the concept of {topic} for a beginner.

    Give output in JSON with keys:
    - definition
    - example
    - use_cases

    {format_instructions}
    """,
                partial_variables={
                    "format_instructions": format_instructions
                }
            )

            chain = prompt | llm
            response = chain.invoke({"topic": topic})

            parsed_output = parser.parse(response.content)

            return Response(parsed_output)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
         

class GoogleGenAIModel(APIView):
    # pip install -U langchain
    # pip install -U langchain-google-genai
    # pip install -U google-genai
    # pip install -U google-generativeai
    def post(self, request):
        topic = request.data.get("topic")

        if not topic:
            return Response({"error": "topic not found"}, status=400)

        try:
            # 2. Replace ChatOpenAI with ChatGoogleGenerativeAI
            # Use "gemini-1.5-flash" for speed or "gemini-1.5-pro" for complex tasks
            llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            temperature=0.7
        )

            parser = JsonOutputParser()
            format_instructions = parser.get_format_instructions()

            prompt = PromptTemplate(
                input_variables=["topic"],
                template="""
                Explain the concept of {topic} for a beginner.
                Give output in JSON with keys:
                - definition
                - example
                - use_cases

                {format_instructions}
                """,
                partial_variables={"format_instructions": format_instructions}
            )

            # 3. LangChain Expression Language (LCEL) stays the same!
            chain = prompt | llm | parser 
            
            # With Gemini, we can pipe the parser directly to get a clean dict
            parsed_output = chain.invoke({"topic": topic})

            return Response(parsed_output)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        


# 1. Tool Definition (Rules + Logic)
class MenuInput(BaseModel):
    meal_type: str = Field(description="The meal time: 'breakfast', 'lunch', or 'dinner'")

@tool(args_schema=MenuInput)
def check_menu(meal_type: str) -> str:
    """Provides the current restaurant menu based on the meal type."""
    menus = {
        "breakfast": "Omelet, Pancakes, and Tea.",
        "lunch": "Biryani, Burger, and Salad.",
        "dinner": "Steak, Pasta, and Soup."
    }
    return menus.get(meal_type.lower(), "Sorry, that menu is not available.")

# 2. Django View Class
class RestaurantAgentView(APIView):
    def post(self, request):
        user_input = request.data.get("input")
        if not user_input:
            return Response({"error": "input field is required"}, status=400)

        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-3-flash-preview", 
                temperature=0.7
            )

            # prompt = ChatPromptTemplate.from_messages([
            #     ("system", "You are a helpful and polite Restaurant Assistant. Use the check_menu tool to answer customers."),
            #     ("human", "{input}"),
            #     MessagesPlaceholder(variable_name="agent_scratchpad"),
            # ])

            system_prompt = "You are a helpful and polite Restaurant Assistant. Use the check_menu tool to answer customers."
            

            @before_model
            def verbose_before(state: AgentState, runtime) -> dict | None:
                print("🤖 LLM Thinking...")
                return None

            @after_model
            def verbose_after(state: AgentState, runtime) -> dict | None:
                last_msg = state["messages"][-1]
                
                # FIXED: Handle dict vs object tool_calls (Gemini format)
                tool_calls = getattr(last_msg, 'tool_calls', [])
                if isinstance(tool_calls, list) and tool_calls:
                    if isinstance(tool_calls[0], dict):  # Gemini dict format
                        print(f"🛠️  Tool calls: {[tc.get('name', 'unknown') for tc in tool_calls]}")
                    else:  # Object format
                        print(f"🛠️  Tool calls: {[tc.name for tc in tool_calls]}")
                else:
                    print(f"💬 Final: {last_msg.content[:100]}...")
                return None

            agent = create_agent(
                model=llm,
                tools=[check_menu],
                system_prompt=system_prompt,
                middleware=[
                    # verbose_before,
                    # verbose_after,
                    ToolCallLimitMiddleware(
                        run_limit=3,           # Max 3 tool calls
                        exit_behavior="end",
                    )
                ]
            )

            # Invoke
            result = agent.invoke({
                "messages": [HumanMessage(content=user_input)]
            })

            return Response({
                "status": "success",
                "output": result["messages"][-1].content
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)