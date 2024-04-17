from rest_framework.views import APIView
from django.http import JsonResponse
from textselection.openai_helper import OpenAIHelper
import os

class TextModifier(APIView):
    def post(self, request):
        text = request.data.get('text')
        option = request.data.get('option')

        if not text or not option:
            return JsonResponse({'status': 'error', 'message': 'Missing text or option'}, status=400)

        prompt = self.create_prompt(text, option)

        openai_key = os.getenv('OPENAI_API_KEY')
        openai_response = OpenAIHelper.generate_text(openai_key, prompt)

        # Process the API response
        if openai_response:
            return JsonResponse({'status': 'success', 'data': openai_response})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to generate response'}, status=400)

    def create_prompt(self, text, option):
       

        if option == 'correct':
            prompt = f"Original text: {text}\n"
            prompt += "Instructions: Correct the grammar and spelling errors in the following text. "
            prompt += "If you don't find any errors, just return the text."
            return prompt


        elif option == 'elaborate':
            max_length = len(text.split()) + 5
            prompt = (f"Original text: '{text}'\n"
                    f"Instructions: Elaborate on the above text without exceeding {max_length} total words.")
            return prompt
        
        elif option == 'shorten':
            if len(text.split()) == 1:
                prompt = f"Original word: '{text}'\n"
                prompt += "Instructions: Provide a shorter word or abbreviation that represents the original word."
            else:
                prompt = f"Original text: '{text}'\n"
                prompt += "Instructions: Summarize the following text in fewer words while retaining the key information."
            return prompt

        elif option == 'rewrite':
            prompt = f"Original text: '{text}'\n"
            prompt += "Instructions: Rewrite the following text to improve clarity and readability while maintaining the same meaning."
            return prompt
        
        else:
            return "No valid option selected."


class RephraseTextView(APIView):
    def post(self, request):
        original_text = request.data.get('text', '')
        if not original_text:
            return JsonResponse({'status': 'failure', 'message': 'No text provided'}, status=400)

        new_prompt = (f"Please rephrase the following text to correct grammatical mistakes and improve sentence structure. "
                  f"Provide the rephrased versions as three separate entries, each in its own array, within a larger array. "
                  f"Each version should retain the same meaning as the original: \n\n"
                  f"'{original_text}'"
                  )

        openai_key = os.getenv('OPENAI_API_KEY')
        rephrased_text = OpenAIHelper.rephrase(openai_key, new_prompt)

        if rephrased_text:
            return JsonResponse({'status': 'success', 'data': rephrased_text})
        else:
            return JsonResponse({'status': 'failure', 'message': 'Response generation failed'}, status=400)



