from typing import List
import langchain
class InstructionGenerationTemplate(langchain.prompts.PromptTemplate):
    """A custom prompt template for generating instructions."""
    
    input_variables: List[str] = ["num_questions", "context", "instruction_format", "lang", "additional_rules"]
    
    template = """
        You are a highly intelligent language model trained to assist with a variety of language tasks. Your task here is to generate {num_questions} diverse questions or instructions based on the context provided below:

        Context:
        {context}

        Please follow these rules:
        {additional_rules}

        Please generate the instructions in the {instruction_format} format and in {lang} language. Remember to adhere to the rules mentioned above.
    """
    template_format = "f-string" 
    def format(self, **kwargs):
        """Format the prompt."""
        return self.template.format(**kwargs)

