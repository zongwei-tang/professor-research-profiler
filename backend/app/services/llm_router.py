import asyncio

import anthropic
from google import genai
from openai import AsyncOpenAI
from fastapi import HTTPException

from app.core.config import settings
from app.core.rate_limit import token_bucket, llm_backup


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


async def llm_process(provider: str, prompt_text: str, original_provider: str | None = None, retry: int = 0):
    if original_provider is None:
        original_provider = provider

    if retry >= 4:
        raise HTTPException(status_code=502, detail="All providers are down")

    match provider:
        case 'openai':
            try:
                if llm_backup[provider].count < 5 and await token_bucket[provider].acquire():
                    client = AsyncOpenAI()
                    response = await client.responses.create(
                        model="gpt-5.5",
                        input=prompt_text,
                    )
                    llm_backup[provider].count = 0
                    return response.output_text, provider
                elif llm_backup[provider].count >= 5:
                    asyncio.create_task(llm_backup[provider].retest())
                    return await llm_process('anthropic', prompt_text, original_provider, retry + 1)
            except Exception:
                if llm_backup[provider].count < 5:
                    llm_backup[provider].count += 1
                return await llm_process(provider, prompt_text, original_provider, retry)
        case 'anthropic':
            try:
                if llm_backup[provider].count < 5 and await token_bucket[provider].acquire():
                    client = anthropic.AsyncAnthropic()
                    message = await client.messages.create(
                        model="claude-opus-4-8",
                        max_tokens=1000,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt_text,
                            }
                        ],
                    )
                    llm_backup[provider].count = 0
                    return message.content[0].text, provider # type: ignore
                elif llm_backup[provider].count >= 5:
                    asyncio.create_task(llm_backup[provider].retest())
                    return await llm_process('deepseek', prompt_text, original_provider, retry + 1)
            except Exception:
                if llm_backup[provider].count < 5:
                    llm_backup[provider].count += 1
                return await llm_process(provider, prompt_text, original_provider, retry)
        case 'deepseek':
            try:
                if llm_backup[provider].count < 5 and await token_bucket[provider].acquire():
                    client = AsyncOpenAI(
                        api_key=settings.deepseek_api_key,
                        base_url="https://api.deepseek.com",
                    )

                    response = await client.chat.completions.create(
                        model="deepseek-v4-pro",
                        messages=[
                            {"role": "user", "content": prompt_text},
                        ],
                        stream=False,
                        reasoning_effort="high",
                        extra_body={"thinking": {"type": "enabled"}},
                    )

                    llm_backup[provider].count = 0
                    return response.choices[0].message.content, provider
                elif llm_backup[provider].count >= 5:
                    asyncio.create_task(llm_backup[provider].retest())
                    return await llm_process('gemini', prompt_text, original_provider, retry + 1)
            except Exception:
                if llm_backup[provider].count < 5:
                    llm_backup[provider].count += 1
                return await llm_process(provider, prompt_text, original_provider, retry)
        case 'gemini':
            try:
                if llm_backup[provider].count < 5 and await token_bucket[provider].acquire():
                    client = genai.Client()

                    response = await client.aio.models.generate_content(
                        model="gemini-3.1-pro",
                        contents=prompt_text,
                    )

                    llm_backup[provider].count = 0
                    return response.text, provider
                elif llm_backup[provider].count >= 5:
                    asyncio.create_task(llm_backup[provider].retest())
                    return await llm_process('openai', prompt_text, original_provider, retry + 1)
            except Exception:
                if llm_backup[provider].count < 5:
                    llm_backup[provider].count += 1
                return await llm_process(provider, prompt_text, original_provider, retry)
