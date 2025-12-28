from typing import Dict , List , Optional , Union , Any, Literal

sources : Union [str , Path , List [ Union [str , Path ]]] ,
doc_types : Optional [ List [ DocumentType ]] = None ,


class SentimentSchema(BaseModel):
    sentiment: Literal["positive", "negative"] = Field(description='Sentiment of the review')


from pydantic import BaseModel,Field, field_validator, model_validator, computed_field
from pydantic import AnyUrl,EmailStr
from typing import List,Dict,Optional,Annotated


class Address(BaseModel):
    city: str
    state: str
    pin: str

class Student(BaseModel):
    address: Address
        
    name: Annotated[str,Field(max_length=50,title='Name of the Student',description= 'Give the name of the student in lessthan 50 character',
                              examples= ['John','Ram'])]
    age: int = Field(gt=8,lt=25)
    height: float  ## mtr   
    weight: Annotated[float,Field(gt=45)]
    married: Annotated[bool, Field(default=None, description='Is the patient married or not')]
    contact_details: Dict[str, str]
        
    allergies: Annotated[Optional[List[str]], Field(default='Nothing', max_length=5)]
    
    email : EmailStr
    linkedin_url: AnyUrl
        
        
    @field_validator('email')
    @classmethod
    def email_validator(cls, value):

        valid_domains = ['gmail.com', 'yahoo.com']
        # abc@gmail.com
        domain_name = value.split('@')[-1]

        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')

        return value
    
    @field_validator('name')
    @classmethod
    def transform_name(cls, value):
        return value.upper()
    
    @field_validator('weight', mode='after')
    @classmethod
    def validate_age(cls, value):
        if 0 < value < 70:
            return value
        else:
            return 40
        
        
    @model_validator(mode='after')
    def validate_emergency_contact(cls, model):
        if model.age < 10 and 'Parents_number' not in model.contact_details:
            raise ValueError('student is minor must have an parents contact number')
        return model
    
    
    
    @computed_field
    @property
    def bmi(cls) -> float:
        bmi = round(cls.weight/(cls.height**2),2)
        return bmi

        
        
address_dict = {'city': 'gurgaon', 'state': 'haryana', 'pin': '122001'}

address1 = Address(**address_dict)

student_info_1 = {
                'address': address1,
                'name':'ironman', 
                'email':'abc@gmail.com',
                'linkedin_url':'http://linkedin.com/1322',
                'age': '23', 
                'weight': 75.2,
                'height' : 1.7, 
                'allergies': ['A','B'],
                'contact_details':{'phone':'1234567890'}}


student_1 = Student(**student_info_1)

print(type(student_1))
temp = student_1.model_dump(exclude_unset=True)
print(type(temp))
print(temp)
