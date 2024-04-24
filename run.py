import os

import torch
from chatbot import Chatbot
import gradio as gr
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, GenerationConfig, TextStreamer, pipeline


if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model_id = 'mistralai/Mistral-7B-Instruct-v0.2'

    token = os.environ['HF_TOKEN']

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type='nf4',
        bnb_4bit_compute_dtype='float16',
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        token=token
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
    generation_config = GenerationConfig.from_pretrained(model_id, token=token)

    streamer = TextStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True, use_multiprocessing=False
    )
    
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=2048,
        temperature=0,
        top_p=0.95,
        repetition_penalty=1.15,
        generation_config=generation_config,
        streamer=streamer,
        batch_size=1,
    )

    llm = HuggingFacePipeline(pipeline=pipe)

    embeddings = HuggingFaceEmbeddings(
        model_name="embaas/sentence-transformers-multilingual-e5-base",
        model_kwargs={"device": device},
    )

    chatbot = Chatbot(llm, embeddings, './data/')

    def get_response(message, history):
        answer = chatbot(message)['answer']
        token = '[/INST]'
        return answer[answer.rfind(token) + len(token):]

    gr.ChatInterface(get_response).launch(share=True)
