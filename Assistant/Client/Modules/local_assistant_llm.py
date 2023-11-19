import openai

def useLocalLLM(host,port):
    openai.api_key = "..."
    openai.api_base = "http://" + host + ":" + port + "/v1"
    openai.api_version = "2023-05-15"

def promptOpenAI(input):
    summary = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-16k',
        # model='llama-2-7b-chat.Q4_0.gguf',
        messages=[{"role":"user", "content": input}]
    )
    return summary.choices[0].message.content + " "


def loadOpenAIKey(keyfile):
    try:
        with open(keyfile, 'r') as f:
            api_key = f.readline().strip()
        return api_key

    except FileNotFoundError:
        print("Key file not found. Please make sure the file exists.")

    except Exception as e:
        print("An error occurred opening the API key file: ", e)

