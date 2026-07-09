import anthropic
import openai
from google import genai
from openai import OpenAI

from app.core.config import settings


def prompt(author, top5, by_year, coauthor, user_interest, language):
    return f"""
        You are an academic research advisor helping PhD applicants evaluate potential supervisors.
        Analyze the following professor's research profile and assess how well they match the applicant's interests.

        ### Professor Basic Information
        {str(author)}

        ### Top 5 Most Cited Papers
        The abstract is the most important field for understanding research direction.
        citationCount reflects academic influence.
        {str(top5)}

        ### Research Fields Over Time
        Papers grouped by year. Use fieldsOfStudy to identify how research focus has shifted.
        {str(by_year)}

        ### Core Collaborators
        The number next to each name is how many papers they co-authored with this professor.
        {str(coauthor)}

        ### Applicant's Research Interests
        {user_interest}

        Based on all the above, please answer the following four questions in {language}.
        Write one full paragraph per question. Use a professional but readable tone, and remember to include questions themselves.

        1. What is this professor's core research direction and academic style?
        2. Has their research focus shifted over time? If so, in what direction?
        3. What are the specific overlaps between the applicant's interests and this professor's work?
        4. Overall, is this professor worth reaching out to? Give a clear recommendation.
        """


def llm_process(provider: str, prompt_text: str):
    match provider:
        case 'openai':
            try:
                client = OpenAI()
                response = client.responses.create(
                    model="gpt-5.5",
                    input=prompt_text,
                )
                return response.output_text
            except openai.OpenAIError:
                return None
        case 'anthropic':
            try:
                client = anthropic.Anthropic()
                message = client.messages.create(
                    model="claude-opus-4-8",
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_text,
                        }
                    ],
                )
                return message.content[0].text
            except anthropic.APIError:
                return None
        case 'deepseek':
            try:
                client = OpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com",
                )

                response = client.chat.completions.create(
                    model="deepseek-v4-pro",
                    messages=[
                        {"role": "user", "content": prompt_text},
                    ],
                    stream=False,
                    reasoning_effort="high",
                    extra_body={"thinking": {"type": "enabled"}},
                )

                return response.choices[0].message.content
            except openai.OpenAIError:
                return None
        case 'gemini':
            try:
                client = genai.Client()

                response = client.models.generate_content(
                    model="gemini-3.1-pro",
                    contents=prompt_text,
                )

                return response.text
            except genai.errors.APIError:
                return None
