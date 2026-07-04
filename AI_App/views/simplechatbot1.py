from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import os

# Gemini Setup
# os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
# llm = ChatGoogleGenerativeAI(model="gemini-pro")

class simplechatbotclass(APIView):
    load_dotenv()
    # 1. GET: Jab user pehli baar page par ayega
    def get(self, request):
        return render(request, 'simplechatbot.html') # Ye aapka frontend file hai

    # 2. POST: Jab user button click karega (AJAX/Fetch request)
    def post(self, request):
        user_question = request.data.get('question')
        
        if not user_question:
            return Response({"error": "Pehle sawal likhain!"}, status=400)
        
        try:
            # Gemini se answer lena
            llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0.7)
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a chatbot"),
                ("human", "{input}")
            ])
            chain = prompt | llm
            result = chain.invoke({"input": user_question})
            if isinstance(result.content, list):
            # Pehla item lo aur uski 'text' key uthao
                final_answer = result.content[0].get('text', '')
            else:
                # Agar direct string hai toh wese hi rehne do
                final_answer = result.content

            return Response({"answer": final_answer}, status=200)
        
        except Exception as e:
            return Response({"error": str(e)}, status=500)