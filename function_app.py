import logging
import azure.functions as func
from openai import AzureOpenAI
import os
import requests

app = func.FunctionApp()

api_key = os.getenv("APIM_OAI_HR_API_KEY")
apim_oai_endpoint = os.getenv("APIM_OAI_ENDPOINT").replace("/openai","")
apim_as_endpoint = os.getenv("APIM_AS_ENDPOINT")

# Set your OpenAI API key here or through application settings
client = AzureOpenAI(
  api_key = api_key,  
  api_version = "2024-05-01-preview",
  azure_endpoint = apim_oai_endpoint
)

@app.function_name(name="QnA-example")
@app.route(route="QnA", auth_level=func.AuthLevel.ANONYMOUS, methods=[func.HttpMethod.POST])
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the question from the request
    try:
        req_body = req.get_json()
        question = req_body.get('question')
    except ValueError:
        return func.HttpResponse("Please pass a question in the request body", status_code=400)

    if not question:
        return func.HttpResponse("The question field is required.", status_code=400)

    try:
        # Call the Azure OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"user", "content":question}
            ]
        )
        answer = response.model_dump_json(indent=2)

        answer = requests.get(url=f"{apim_as_endpoint}/indexes/hotels-sample-index/docs/$count?api-version=2023-11-01")

        # Return the response
        return func.HttpResponse(answer, status_code=200)
    except Exception as e:
        logging.error(f"Error while processing the request: {e}")
        return func.HttpResponse(f"There was an error processing your request: {apim_oai_endpoint}{e}", status_code=500)