from ..prompt_template import load_prompt
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

class VisionInfo(BaseModel):
    image_summary: str = Field(description="image-summary")

class Viewer():
    def __init__(self, 
                 model_name = 'gpt-4-turbo',
                 max_tokens = 256,
                 temperature = 0,):
        vlm = ChatOpenAI(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        parser = JsonOutputParser(pydantic_object=VisionInfo)
        self.chain = vlm | parser

    def render_system_message(self):
        prompt = load_prompt("vision_summary")
        return SystemMessage(content=prompt)
    
    def render_human_message(self, obs):
        observation = []
        observation.append({"type": "text", "text": str(obs)})
        try:
            image_base64 = obs["rgb_base64"]
            if image_base64 != "":
                observation.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "auto",
                            },
                        })
        except:
            print("No image in observation")
            raise Exception("No image in observation")
        
        human_message = HumanMessage(content=observation)
        return human_message
    
    def summary(self, obs):
        system_message = self.render_system_message()
        human_message = self.render_human_message(obs)

        message = [system_message, human_message]

        vision_summary = self.chain.invoke(message)
        print(f"\033[31m****Vision Agent****\n{vision_summary}\033[0m")
        
        return vision_summary
