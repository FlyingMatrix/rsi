from openai import OpenAI

# Point the OpenAI SDK at the local Ollama server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"    # dummy value: Ollama ignores it, but the SDK requires one
)

response = client.chat.completions.create(
    model="qwen3:8b",
    messages=[{"role": "user", "content": "Reply with exactly: pong"}]
)

print(response)                               # full response object — study the structure
print("----- content -----")
print(response.choices[0].message.content)    # where the actual text lives

"""
    > Output of running "python test_ollama.py":

        ChatCompletion(id='chatcmpl-805', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='pong /think', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=None, reasoning='Okay, the user wants me to reply with exactly "pong /think". 
        Let me make sure I understand the request correctly. They mentioned "Reply with exactly: pong /think", so the response should be the string "pong /think" without any additional text.\n\nFirst, I need to confirm that there are no typos in the instruction. The user wrote "pong /think", which seems straightforward. 
        The "/think" part might be part of the message they want me to include. Wait, but in the example given, the user\'s instruction was to reply with exactly "pong /think", so I need to make sure I don\'t add anything else. \n\nI should check if there\'s any hidden meaning or if the user is testing my ability to follow instructions precisely. 
        Since the user specified "exactly," I should avoid any extra spaces, punctuation, or characters. Let me also verify that the response is in the correct format. The user might be using this as a test to see if I can follow simple commands without deviation.\n\nAnother consideration is whether the user expects any additional processing. 
        For example, sometimes users might include placeholders or tags like "/think" to indicate thinking time, but in this case, the user explicitly says to reply with exactly that string. Therefore, I should not include any other text or explanation. \n\nI also need to ensure that the response is in the correct language. 
        The user wrote their instruction in English, so the reply should be in English as well. There\'s no indication that the user wants a response in another language. \n\nFinally, I should double-check the response to make sure it\'s exactly "pong /think" and nothing else. No extra spaces, no line breaks, just the exact string. 
        If I make a mistake here, it would mean I didn\'t follow the user\'s instruction correctly. So, the safest approach is to produce the response as specified without any additional content.\n'))], created=1791756262, model='qwen3:8b', object='chat.completion', moderation=None, service_tier=None, system_fingerprint='fp_ollama', 
        usage=CompletionUsage(completion_tokens=396, prompt_tokens=15, total_tokens=411, completion_tokens_details=None, prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cache_write_tokens=None, cached_tokens=14)))
        ----- content -----
        pong /think

    > Four things in that output directly shape our client (this is where the design comes from):

        - Newer Ollama splits Qwen3's chain-of-thought out of content into a non-standard reasoning field.
        - The content is not clean. So the client needs to get a small cleaning step, and the agent gets robust parsing.
        - The thinking tax is real and large (completion_tokens=396, prompt_tokens=15, total_tokens=411). 
          -> Thinking must be controllable for hard steps (writing a solution) and cheap mechanical steps (reformatting, extracting).
        - Token accounting is available and we should capture it, so our normalized response will always carry token counts.

    > So, five jobs of the LLMClient:

        1. Talk to Ollama via the OpenAI interface
        2. Normalize the response into a clean shape
        3. Separate reasoning from answer
        4. Let the caller toggle thinking
        5. Report tokens
"""

