import json
import re
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import JSONLoader

class VectorDB:
    def __init__(self, data_path):
        self.loader = TextLoader(data_path)
        self.documents = self.loader.load() 
        # - /Users/vishanee/langChain/hackathon/RAG/c1_rag_backend/attachments/text.txt
        jq_schema = ".[]"  # Adjust this based on your JSON structure
        # if not data_path:
        #     data_path = "/Users/vishanee/langChain/hackathon/RAG/c1_rag_backend/attachments/PRODUCT_OFFERING.json"
        # self.loader = JSONLoader(data_path, jq_schema=jq_schema, text_content=False)
        # self.documents = self.loader.load()
        print("Documents loaded")

        self.text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        self.chunks = self.text_splitter.split_documents(self.documents)

        self.vectorstore = FAISS.from_documents(
            documents=self.chunks,
            embedding=OllamaEmbeddings(model="nomic-embed-text")
        )

        self.retriever = self.vectorstore.as_retriever()

        self.template = """
**Instructions:**

Role: act as Document Analyzer
 
Task:
Analyze the provided document, get its meaning and format and convert it to proper text format and reply to the answer on relevant format with explanation.
 
Examples:
 
Format:
 
Restriction:
Provide all reliable data with citations using file names. Don't mentions type of file unless asked. Don't expand acronymns unless full-form is mentioned in context.
 
Additional:
think step-by-step.  generate at a good level of detail, with clear and well-defined outpout.
The structure of the response is also easy to follow, and it provides relevant source references and includes a step-by-step explanation,
which makes it easier to understand the process and implement the solution. presents a comprehensive approach.

**BEGIN PROCESSING:**

**Context:**
{context}

**Field Name:**
{field_name}

**Action:**
{domain_action}

**Question:**
{question}

        """
        self.prompt = ChatPromptTemplate.from_template(self.template)

        self.llm = ChatOllama(model="gemma3:1b", temperature=0.7)

        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough(),  "field_name": RunnablePassthrough(), "domain_action": RunnablePassthrough()} 
            | self.prompt 
            | self.llm 
            | StrOutputParser()
        )

    def query_vector_db(self, query):
        """
            Queries the vector database.

            Args:
                query (dict): A dictionary containing the question and field name.

            Returns:
                str: The result of the query.
            """
        print(f"Query received: {query}")
        if "field_name" not in query:
             print("Error: 'field_name' is missing in the query.")
             return "Invalid query: 'field_name' is required."

    # Add 'field_name' to the input for the rag_chain
        input_data = {
             "context": self.retriever,  # Retrieves relevant context
             "question": query["question"],
             "field_name": query["field_name"],
             "domain_action": query["domain_action"] 
        }

        try:
            result = self.rag_chain.invoke(input_data)
            print(f"LLM Response: {result}")
            return result
        except Exception as e:
            print(f"Error invoking LLM: {str(e)}")
            return {"error": str(e)}

    def clear_vector_db(self):
        """
        Clears the vector database by resetting the FAISS index.
        """
        if not self.chunks or len(self.chunks) == 0:
            print("No documents to clear. Vector database is already empty.")
            return
        try:
            self.vectorstore = FAISS.from_documents(
                documents=[],  # Resetting with an empty list
                embedding=OllamaEmbeddings(model="nomic-embed-text")
            )
            self.retriever = self.vectorstore.as_retriever()
            print("Vector database cleared.")
        except Exception as e:
            print(f"Error while clearing vector database: {str(e)}")

class PromptProcessor:
    def __init__(self, vector_db_path):
        self.vector_db = VectorDB(vector_db_path)
        
    def format_llm_response(self, response):
        """
        Formats the LLM response into the expected structure.

        Args:
        response (dict): The raw response from the LLM.

    Returns:
        str: The formatted response.
        """
        raw_result = response.get("result", "")
    
        # Extract the <think> section
        think_pattern = re.search(r"<think>(.*?)</think>", raw_result, re.DOTALL)
        think_text = think_pattern.group(1).strip() if think_pattern else "No <think> section found."

        # Extract the fields section after </think>
        fields_pattern = re.search(r"</think>\n(.*)", raw_result, re.DOTALL)
        fields_text = fields_pattern.group(1).strip() if fields_pattern else "No fields section found."

        # Format the <think> section
        formatted_think = f"LLM Response: <think>\n{raw_result}\n</think>\n\n"

        # Format the fields section
        formatted_fields = ""
        for line in raw_result.split("\n"):
            if line.startswith("- "):  # Format list items
                formatted_fields += f"- **{line[2:]}**\n"
            elif line.startswith("###"):  # Format headings
                formatted_fields += f"{line}\n"
            elif line.strip():  # Add other lines as plain text
                formatted_fields += f"   {line.strip()}\n"

        return formatted_fields

    def process_prompt(self, prompt, domain_action,field_name):
        query = {
            "question": prompt, 
            "field_name": field_name,
            "domain_action" : domain_action
        }
        
        result = self.vector_db.query_vector_db(query)
        if result == "Not Found":
            self.vector_db.clear_vector_db()  # Clear the vector database
            return {"result": "Not Found"}

        # Attempt to parse the result as JSON
        try:
            result_json = json.loads(result)
            self.vector_db.clear_vector_db()  # Clear the vector database
            return result_json
        except json.JSONDecodeError:
            # If parsing fails, return the result as is
            # self.vector_db.clear_vector_db()  # Clear the vector database
            formatted_result = self.format_llm_response({"result": result})
            return formatted_result
        except Exception as e:
            return {"error": str(e)}

# Example usage
if __name__ == '__main__':
    vector_db_path = '/Users/vishanee/langChain/hackathon/RAG/c1_rag_backend/text.txt'
    prompt_processor = PromptProcessor(vector_db_path)

    # Example prompt and field name
    user_prompt = "What is the product offering type?"
    field_name = "productOfferingType"
    
    response = prompt_processor.process_prompt(user_prompt, field_name)
    print(response)
