
from unittest.mock import Mock
from openai import APIConnectionError
import httpx

# Create a fake API client
fake_client = Mock()

# Create a fake network request
request = httpx.Request(
    "POST",
    "https://api.openai.com/v1/responses"
)

# First request fails, second succeeds
fake_client.responses.create.side_effect = [
    APIConnectionError(request=request),
    Mock(output_text="Three recipes generated!")
]

# Test retry logic
def test_retry():
    for attempt in range(2):
        try:
            response = fake_client.responses.create()
            print(response.output_text)
            break

        except APIConnectionError:
            print("Temporary connection error!")

            if attempt == 0:
                print("Retrying...")
            else:
                print("Both attempts failed.")

    print(
        "API calls:",
        fake_client.responses.create.call_count
    )

test_retry()
