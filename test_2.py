import os
import streamlit as st
import boto3
import json
from datetime import datetime
import subprocess

# Amazon Bedrock Client (Only used for generating the test case, no unwanted API calls)
bedrock = boto3.client(service_name="bedrock-runtime")

# Directory to save scripts
SCRIPT_DIR = "generated_scripts"
os.makedirs(SCRIPT_DIR, exist_ok=True)  # Ensure the directory exists

def generate_script_filename():
    """Generate a filename with date and time."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(SCRIPT_DIR, f"script_{timestamp}.py")

def save_selenium_script(selenium_script):
    """Save the Selenium script and return its file path."""
    file_path = generate_script_filename()
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(selenium_script)
    
    # Set the script path as an environment variable for Robot Framework
    os.environ["SELENIUM_SCRIPT"] = file_path
    
    st.success(f"✅ Script saved and environment variable set: {file_path}")
    return file_path

def run_robot_framework():
    """Run the Robot Framework test case."""
    try:
        result = subprocess.run(["robot", "trial.robot"], capture_output=True, text=True, check=True)
        st.text_area("Robot Framework Output:", result.stdout + result.stderr, height=300)
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Error running Robot Framework: {e.output}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")

def generate_test_case(user_instruction):
    """Generate a test case from user instructions."""
    prompt_data = f"""
    You are an expert in software testing. Generate a detailed test case.
    Instruction:
    {user_instruction}
    Output Format:
    ```plaintext
    Test Case: <Title>
    Test Steps:
    1. <Step 1>
    Expected Result:
    - <Expected Outcome>
    ```
    """
    
    response = bedrock.invoke_model(
        modelId="amazon.nova-pro-v1:0",
        accept="application/json",
        contentType="application/json",
        body=json.dumps({
            "inferenceConfig": {"max_new_tokens": 1500},
            "messages": [{"role": "user", "content": [{"text": prompt_data}]}]
        })
    )
    
    response_body = json.loads(response["body"].read().decode("utf-8"))
    return response_body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "").strip("```plaintext")

def generate_prompt(test_cases): 
    website_url = "https://www.saucedemo.com/"

    prompt_data = f"""
    You are an expert in **test automation**. Given a set of test cases, generate a **Python Selenium script** that automates the described test steps with delays for visibility.

    ## **Website:** SauceDemo  
    - **URL:** {website_url}

    ## **Requirements:**
    - Use **Selenium with Python**.
    - Use **webdriver-manager** to manage WebDriver.
    - Use **Service() with webdriver.Chrome()** to initialize WebDriver correctly.
    - Follow best practices for **locating elements** (XPath, CSS selectors, ID, etc.).
    - Ensure scripts include proper **wait conditions** (explicit waits) for reliability.
    - Use **WebDriverWait with expected_conditions** to wait for elements dynamically.
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
    4. **Use `WebDriverWait` and `expected_conditions` to handle dynamic elements**.
    5. **Introduce a `time.sleep(2)` delay after each action** for visibility.
    6. **Log each action before execution** using `print()`.
    7. **Verify expected behavior using assertions**.
    8. **Handle navigation and user interactions efficiently**.
    9. **Log results or screenshots if needed**.
    10. **Keep the browser open until the user presses Enter.**

    ### **Additional Handling**
    - If an element is **not immediately available**, use **explicit waits** instead of direct `find_element()`.
    - If an element is missing, try **alternative locators** (XPath, ID, CSS).
    - Implement **exception handling** to prevent abrupt failures.
    - Each test step should have a **`time.sleep(2)` delay** to visually see the execution.

    Provide only the **Python Selenium script** without additional explanations.

    **Output Format:**
    ```python
    import time
    
    # Python Selenium script starts here
    <Your Generated Selenium Code>

    # Introduce delays after each step
    time.sleep(2)

    # Keep browser open until user presses Enter
    input("Press Enter to close the browser...")
    driver.quit()

    # Python Selenium script ends here
    ```
    """
    return prompt_data

def get_selenium_script(test_case):
    """Generate a Selenium script from a test case."""
    prompt_data = generate_prompt(test_case)
    
    response = bedrock.invoke_model(
        modelId="amazon.nova-pro-v1:0",
        accept="application/json",
        contentType="application/json",
        body=json.dumps({
            "inferenceConfig": {"max_new_tokens": 5000},
            "messages": [{"role": "user", "content": [{"text": prompt_data}]}]
        })
    )
    
    response_body = json.loads(response["body"].read().decode("utf-8"))
    return response_body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "").strip("```python")

# Streamlit UI
st.title(" TestGenie 🧞‍♂️ ")
input_option = st.radio("Choose an option:", ("Upload File", "Enter Manually"))

test_case_input = ""
user_instruction_input = ""

if input_option == "Upload File":
    uploaded_file = st.file_uploader("Upload a test case or user scenario file", type=["txt", "md"])
    
    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")
        if "Test Case:" in file_content:
            test_case_input = file_content
        else:
            user_instruction_input = file_content
            test_case_input = generate_test_case(user_instruction_input)
elif input_option == "Enter Manually":
    manual_entry_type = st.radio("What do you want to enter?", ("Test Case", "User Scenario"))
    if manual_entry_type == "Test Case":
        test_case_input = st.text_area("Enter your test case:", height=300)
    elif manual_entry_type == "User Scenario":
        user_instruction_input = st.text_area("Describe the scenario to generate a test case:", height=300)
        if user_instruction_input.strip():
            test_case_input = generate_test_case(user_instruction_input)
            st.subheader("Generated Test Case")
            st.text_area("Generated Test Case:", test_case_input, height=300)

if test_case_input.strip():
    selenium_script = get_selenium_script(test_case_input)
    if selenium_script:
        script_path = save_selenium_script(selenium_script)
        st.subheader("Generated Selenium Script")
        st.code(selenium_script, language="python")
        st.download_button("⬇️ Download Selenium Script", selenium_script, file_name=os.path.basename(script_path))
        run_robot_framework()
