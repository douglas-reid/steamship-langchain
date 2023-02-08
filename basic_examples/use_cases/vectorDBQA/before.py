from pathlib import Path

from langchain import OpenAI
from langchain.chains import VectorDBQAWithSourcesChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

# index a file
with Path("state_of_the_union.txt").open() as f:
    state_of_the_union = f.read()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_text(state_of_the_union)

embeddings = OpenAIEmbeddings()
docsearch = FAISS.from_texts(texts,
                             embeddings,
                             metadatas=[{"source": i} for i in range(len(texts))])

query = "What did the president say about Justice Breyer"
searched_docs = docsearch.similarity_search(query)
for doc in searched_docs:
    print(doc)

chain = VectorDBQAWithSourcesChain.from_chain_type(OpenAI(temperature=0),
                                                   chain_type="stuff",
                                                   vectorstore=docsearch)

output = chain({"question": "What did the president say about Justice Breyer"}, return_only_outputs=True)
print(output)

chain = VectorDBQAWithSourcesChain.from_chain_type(OpenAI(temperature=0),
                                                   chain_type="map_reduce",
                                                   vectorstore=docsearch)

output = chain({"question": "What did the president say about Justice Breyer"}, return_only_outputs=True)

print(output)

chain = load_qa_with_sources_chain(OpenAI(temperature=0),
                                   chain_type="map_reduce",
                                   return_intermediate_steps=True)

output = chain({"input_documents": searched_docs, "question": query}, return_only_outputs=True)
print(output)
