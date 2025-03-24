import streamlit as st
import boto3
import json
import os

def generate_prompt(test_cases): 
    website_url = "https://www.saucedemo.com/"

    prompt_data = f"""
    You are an expert in **test automation**. Given a set of test cases, generate a **Python Selenium script** that automates the described test steps.

    ## **Website:** SauceDemo  
    - **URL:** {website_url}

    ## **Requirements:**
    - Use **Selenium with Python**.
    - Use **webdriver-manager** to manage WebDriver.
    - Use **Service() with webdriver.Chrome()** to initialize WebDriver correctly.
    - Follow best practices for **locating elements** (XPath, CSS selectors, ID, etc.).
    - Ensure scripts include proper **wait conditions** (explicit waits) for reliability.
    - Include **assertions** to validate expected outcomes.
    - Make the script **modular** by defining functions for each test step.
    - The script should handle **dynamic elements**, popups, and navigation efficiently.
    - Allow **parameterization** of test inputs (e.g., credentials, product names).
    - Handle **multiple test scenarios** efficiently.

    ---

    ## **Test Cases:**
    {test_cases}

    ---

    ## **Expected Output:**
    A well-structured **Python Selenium script** implementing the above test cases. The script should:
    1. **Initialize WebDriver using `Service()`**.
    2. **Navigate to the website (`{website_url}`)**.
    3. **Perform test actions** as described in the test cases.
    4. **Verify expected behavior using assertions**.
    5. **Handle navigation and user interactions efficiently**.
    6. **Log results or screenshots if needed**.
    7. **Keep the browser open** if required by the test case.

    - Handle cases where elements are not immediately available.
- If an element is missing, try alternative locators.
- Implement exception handling to prevent abrupt failures.


    Provide only the **Python Selenium script** without additional explanations.

    **Output Format:**
    ```python
    # Python Selenium script starts here
    <Your Generated Selenium Code>
    # Python Selenium script ends here
    ```
    """
    return prompt_data

bedrock = boto3.client(service_name="bedrock-runtime")


def get_selenium_script(test_cases):
    prompt_data = generate_prompt(test_cases)
    payload = {
        "modelId": "amazon.nova-pro-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "inferenceConfig": {
                "max_new_tokens": 3000  
            },
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": " "+prompt_data+"."
                        }
                    ]
                }
            ]
        })
    }

    response = bedrock.invoke_model(
        modelId=payload["modelId"],
        accept=payload["accept"],
        contentType=payload["contentType"],
        body=payload["body"]
    )
    response_body = json.loads(response["body"].read().decode("utf-8"))
    #st.write(response_body) 


    try:
        generated_script = response_body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "")

    except (KeyError, IndexError, TypeError):
        st.error("❌ Error: Could not extract the generated script from response.")
        return None

    if generated_script.startswith("```python"):
        generated_script = generated_script[9:]  # Remove leading ```python
    if generated_script.endswith("```"):
        generated_script = generated_script[:-3] 
    
    return generated_script

# import streamlit as st
# import requests

# FLASK_SERVER_URL = "http://127.0.0.1:5000"

import streamlit as st
import requests

RECEIVER_ENDPOINT = "https://1fab-14-140-179-66.ngrok-free.app/run_selenium"

st.title("TestGenie 🧞‍♂️")

uploaded_file = st.file_uploader("Upload a test case file (.txt or .md)", type=["txt", "md"])
test_cases = ""

if uploaded_file is not None:
    test_cases = uploaded_file.read().decode("utf-8")

# Manual Input Option
test_case_input = st.text_area("Or enter test cases manually:", test_cases, height=300)

# Generate & Send Button
if st.button("Generate & Send Selenium Script"):
    if test_case_input.strip():
        selenium_script = get_selenium_script(test_case_input)

        # Display Generated Script
        st.subheader("Generated Selenium Script")
        st.code(selenium_script, language="python")

        # 🔹 Automatically send the script to the receiver's API
        try:
            response = requests.post(RECEIVER_ENDPOINT, json={"script": selenium_script}, timeout=30)

            if response.status_code == 200:
                st.success("✅ Script sent successfully!")
            else:
                st.error(f"❌ Failed to send script. Server responded with: {response.status_code}")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error: {e}")

    else:
        st.warning("⚠️ Please enter or upload a test case.")
