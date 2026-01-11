import boto3
import os

# Set Parameters
model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Initialize AWS Bedrock client
bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# Loop until user enters "quit"
while True:
    # Query to send to Claude
    query = input("👤 Enter your query (or 'quit' to exit): ")
    
    # Check if user wants to quit
    if query.lower() == "quit":
        print("Goodbye!")
        break
    
    # Make the API call using Converse API
    try:
        print("🤖 System call")
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": query}]
                }
            ],
            inferenceConfig={"maxTokens": 1024}
        )
        
        # Extract and print the response
        output = response['output']['message']['content'][0]['text']
        print(f"👤 Query: {query}")
        print(f"\nResponse:\n{output}\n")
        
    except Exception as e:
        print(f"Error calling Bedrock: {e}\n")

