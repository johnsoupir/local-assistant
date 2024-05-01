#!/bin/bash

sudo apt install -y espeak


#Install python reqs
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

#Install python bindings of llama.cpp
NEW_GPU="https://github.com/abetlen/llama-cpp-python.git"
PASCAL="https://github.com/johnsoupir/llama-cpp-python-pascal.git"

echo "#### Do you have a Pascal GPU? P40, P100, etc.."
echo "Enter y or n: "
read GPU_TYPE

if [[ $GPU_TYPE == "y" ]]
then 
    echo "PASCAL INSTALL"
    git clone --recurse-submodules $PASCAL
    cd llama-cpp-python-pascal
else
    echo "NORMAL INSTALL"
    pip install llama-cpp-python
fi



#Download default model
echo "DOWNLOADING LLM MODEL"
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.Q4_K_M.ggufhttps://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf

