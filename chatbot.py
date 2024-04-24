from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter

DEFAULT_TEMPLATE = """
<s>[INST]
Instruction: You're an expert in international student and immigration services at NYU.

Use only the chat history and the following information

{context}

to answer in a helpful manner to the question. If you don't know the answer - say that you don't know. Keep your replies short, compassionate and informative.

{chat_history}

Question: {question}
[/INST]
""".strip()
 
 
class Chatbot:
    def __init__(
        self,
        text_pipeline: HuggingFacePipeline,
        embeddings: HuggingFaceEmbeddings,
        documents_dir: str,
        prompt_template: str = DEFAULT_TEMPLATE,
        verbose: bool = False,
    ):
        prompt = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template=prompt_template,
        )
        self.db = self._embed_data(documents_dir, embeddings)
        self.qa = ConversationalRetrievalChain.from_llm(
            text_pipeline,
            self.db.as_retriever(),
            combine_docs_chain_kwargs={"prompt": prompt},
            verbose=verbose
        )
 
    def _embed_data(
        self, documents_dir: str, embeddings: HuggingFaceEmbeddings
    ) -> Chroma:
        loader = DirectoryLoader(documents_dir, glob="**/*txt")
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        return Chroma.from_documents(texts, embeddings)
 
    def __call__(self, user_input: str) -> str:
        return self.qa({'question': user_input, 'chat_history': []})
    