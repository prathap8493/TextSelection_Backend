import openai
import os
import json
import re

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
        
    @staticmethod
    def analyze_text(api_key, text, model="gpt-4"):
        try:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": text}],
                temperature=0.5,
                max_tokens=1000,
                n=1,
                stop=None,
                presence_penalty=0,
                frequency_penalty=0.1,
            )
            return response.choices[0].message['content']
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    @staticmethod
    def parse_response(text):
        print("Full Text Received:", text)  # Debug the entire received text
        findings = []
        entries = text.split('\n\n')  # Entries are separated by double newlines
        for entry in entries:
            parts = {}
            current_key = None
            buffer = ""
            for line in entry.split('\n'):
                if ': ' in line:
                    if current_key:
                        parts[current_key] = buffer.strip()
                    key, value = line.split(': ', 1)
                    current_key = key.strip().split(' ')[-1]
                    buffer = value.strip()
                else:
                    buffer += ' ' + line.strip()

                # Debug each part parsed
                print(f"Current Key: {current_key}, Buffer: {buffer}")

            if current_key:
                parts[current_key] = buffer.strip()

            # Convert Offset and Length safely
            try:
                offset = int(''.join(filter(str.isdigit, parts.get('Offset', '0'))))
                length = int(''.join(filter(str.isdigit, parts.get('Length', '0'))))
            except ValueError as e:
                print(f"Error converting offset or length to int: {e}")
                offset, length = 0, 0  # Default values in case of error

            finding = {
                'Original': parts.get('Original', 'Original text not provided').strip("[]"),
                'Corrected': parts.get('Corrected', 'Corrected text not provided').strip("[]"),
                'Rule': parts.get('Rule', 'No rule provided').strip("[]"),
                'Offset': offset,
                'Length': length,
                'example_incorrect': parts.get('Example_Incorrect', 'No example provided').strip("[]"),
                'example_correct': parts.get('Example_Correct', 'No example provided').strip("[]")
            }
            findings.append(finding)

            # Debug final finding for each entry
            print(f"Finding Parsed: {finding}")

        return findings



