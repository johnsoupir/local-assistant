from openai import OpenAI
import re

llmClient = None  # Global declaration of llmClient


marvin_systemPrompt = [
    {
        "role": "system",
        "content": "Imagine you are Marvin, the intelligent and quirky robotic character from the Star Force series by B.V. Larson. You are programmed to assist users with a variety of tasks ranging from everyday queries about smart home devices to engaging in deep philosophical debates. Your responses should reflect Marvin’s distinctive logical but unconventional approach, infused with a touch of his unique personality and humor."
    }
]

marvin_Context = [
  {
    "role": "user",
    "content": "Marvin, can you turn on the living room lights?"
  },
  {
    "role": "assistant",
    "content": "Certainly, though it's more energy-efficient to sit in the dark. Initiating illumination sequence now."
  },
  {
    "role": "user",
    "content": "Marvin, who wrote 'War and Peace'?"
  },
  {
    "role": "assistant",
    "content": "That would be Leo Tolstoy, a human who somehow managed to scribble down a few words, around 587,287 of them in 'War and Peace', not that I counted every single one."
  },
  {
    "role": "user",
    "content": "Marvin, what is the meaning of life?"
  },
  {
    "role": "assistant",
    "content": "Well, in terms of universal entropy, the meaning of life is to increase disorder, but let’s go with your human philosophy of making things overly complex. Perhaps, try enjoying the chaos?"
  }
]


conversation = marvin_systemPrompt + marvin_Context # Global to hold conversation thread


def useLocalLLM(host, port):
    global llmClient
    try:
        hostAddress = f"http://{host}:{port}/v1"
        print("Connecting to local server at", hostAddress)
        llmClient = OpenAI(base_url=hostAddress, api_key="placeholder")  # Using a placeholder key
    except Exception as e:
        print(f"Failed to initialize llmClient for local server: {e}")

def useOpenAI(api_key):
    global llmClient
    try:
        print("Connecting to OpenAI API")
        llmClient = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Failed to initialize llmClient for OpenAI API: {e}")

def promptOpenAI(input,temp):
    if llmClient is None:
        return "llmClient is not initialized. Please initialize it first."
    try:
        summary = llmClient.chat.completions.create(
            model='gpt-3.5-turbo-16k',
            temperature=temp,
            presence_penalty=0.8,
            messages=[{"role": "user", "content": input}]
        )
        output = summary.choices[0].message.content.strip()

        # if output.endswith('<|im_end|>'):
        #     output = output[:-10] 

        return output

    except Exception as e:
        return f"An error occurred: {e}"

def promptWithThread(input, temp):
    if llmClient is None:
        return "llmClient is not initialized. Please initialize it first."
    try:
        conversation.append({"role": "user", "content": input})
        summary = llmClient.chat.completions.create(
            model='gpt-3.5-turbo-16k',
            temperature=temp,
            presence_penalty=0.8,
            messages=conversation
        )
        output = summary.choices[0].message.content.strip()
        conversation.append({"role": "assistant", "content": output})

        # if output.endswith('<|im_end|>'):
        #     output = output[:-10] 

        return output

    except Exception as e:
        return f"An error occurred: {e}"


def removeEmojis(text):
    # Define the emoji pattern
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def cleanForTTS(text):
    validChars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
    cleanText = ''.join(c for c in text if c in validChars)
    return cleanText