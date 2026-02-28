from langchain_ollama import OllamaLLM


llm = OllamaLLM(model="llama3")


response = llm.invoke("What is LangChain? Answer in one sentence doesnt the ollma do same thing.")

print(response)
