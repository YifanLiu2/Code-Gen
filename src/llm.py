from openai import OpenAI
import abc, json
from config import API_KEY

class LLM(abc.ABC):
    def __init__(self):
        pass
    
    @abc.abstractmethod
    def generate(self, message, max_tokens=4000):
        pass

    def parse_json(self, response: str) -> dict:
        json_start, json_end = response.find('{'), response.rfind('}') + 1

        try:
            out = response[json_start:json_end]
            out = json.loads(out)
        except Exception as e:
            print(e)
            print(response)
            return None
        
        return out
        

class GPTChat(LLM):
    def __init__(self, model_name='gpt-4-turbo', api_key=API_KEY):
        super().__init__()
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = model_name


    def generate(self, message, max_tokens=4000, temperature=0.0, json=True):
        kwargs = {}
        if json:
            kwargs["response_format"]={"type": "json_object"}
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=message,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        except Exception as e:
            print(e)
            return None
        return response.choices[0].message.content