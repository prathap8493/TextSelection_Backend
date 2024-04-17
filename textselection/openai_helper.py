import openai
import os


class OpenAIHelper:

    @staticmethod
    def generate_text(openai_key, prompt, engine="gpt-3.5-turbo"):
        try:

            openai.api_key = openai_key
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=650,
                n=1,
                stop=None,
                presence_penalty=0,
                frequency_penalty=0.1,
            )
            message = response['choices'][0]['message']['content']
            return message
        except Exception as e:
            print(f"exception:{str(e)}")
            return "Couldn't Process: Please try shortening or varying your message and resubmitting."
        
    @staticmethod
    def rephrase(api_key, text, model="gpt-3.5-turbo"):
        try:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": text}],
                temperature=0.5,
                max_tokens=650,
                n=1,
                stop=None,
                presence_penalty=0,
                frequency_penalty=0.1,
            )
            message = response.choices[0].message.content
            return message
        except Exception as e:
            print(f"Error: {str(e)}")
            return "Error processing your request. Try modifying your text and resubmitting."