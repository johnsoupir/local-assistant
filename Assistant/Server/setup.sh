#!/bin/bash

sudo apt install espeak


#Install python reqs
pip install -r requirements.txt

#Install python 
git clone --recurse-submodules https://github.com/johnsoupir/llama-cpp-python-pascal.git
cd llama-cpp-python-pascal

#clone text-gen-webui 
git clone https://github.com/oobabooga/text-generation-webui.git

echo "DOWNLOADING LLM MODEL"
cd text-generation-webui/models
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.Q4_K_M.gguf

cd ..

echo "\n\n\n"
echo "TEXT GEN WEBUI WILL BE SET UP NEXT. WHEN PROMPTED SELECT YOUR GPU TYPE."
echo "ENTER TO CONTINUE"
echo "\n\n\n"
read 


./start_linux.sh --listen --api --model modelspython -m bark --text "Hello, my name is Suno." --output_filename "example.wav"/llama-2-7b-chat.Q4_K_M.gguf