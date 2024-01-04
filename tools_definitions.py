from langchain.agents import tool
from langchain.llms import OpenAI
from langchain_experimental.llm_symbolic_math.base import LLMSymbolicMathChain
@tool
def symbolic_math(calculation_request: str) -> str:
    """
    Executes symbolic mathematical calculations using a language model and python. This function takes a string
    input describing a mathematical calculation request and processes it using a symbolic math chain.

    Args:
        calculation_request (str): A string representing the mathematical calculation to be performed.
         This should be a symbolic math problem or expression that can be interpreted by the language model.

    Returns:
        str: The result of the symbolic math calculation.

    Example:
        result = symbolic_math("Integrate x^2 from x=0 to x=5")
        print(result)  # Outputs 125/3
    """
    llm = OpenAI(temperature=0)
    llm_symbolic_math = LLMSymbolicMathChain.from_llm(llm)
    return llm_symbolic_math.run(calculation_request)