from os import listdir, getenv
from json import load
from dotenv import load_dotenv
from typing import Iterator
import openai


def load_environment(env_path: str):
    load_dotenv(dotenv_path=env_path)
    openai.api_key = getenv("OPENAI_ACCESS_TOKEN")

def load_reference():
    with open('reference.json', 'r') as file:
        data = load(file)
    return data

def list_files(directory: str) -> list:
    return [f for f in listdir(directory) if f.endswith(".pdf")]

def chunks(xs: list, n: int) -> Iterator[list]:
    """ Splits input list into len(xs)/n lists of n elements
    """
    n = max(1,n)
    return (xs[i:i+n] for i in range(0, len(xs), n))