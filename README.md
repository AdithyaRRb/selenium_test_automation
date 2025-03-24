#Test Genie
# Flask-Based Selenium Test Automation API

## Overview
This project provides a Flask-based API for managing and executing Selenium automation scripts. It allows users to:
- Upload test cases or user scenarios to generate test cases automatically.
- Generate Selenium scripts from provided test cases.
- View, download, and execute Selenium scripts remotely.
- Keep the browser open after execution for manual interaction.

This solution is ideal for automated UI testing, DevOps pipelines, and remote test execution.

## Features

1. **Upload & Process Test Cases or User Scenarios**
   - Users can upload test cases directly or provide a user scenario.
   - If a test case is uploaded, it is passed directly for Selenium script generation.
   - If a user scenario is uploaded, the system automatically generates test cases and converts them into Selenium scripts.

2. **Generate Selenium Scripts**
   - The system uses AWS Bedrock (Titan LLM) to generate Selenium scripts from test cases.
   - Ensures best practices: modular structure, explicit waits, assertions, and efficient element handling.

3. **Flask API for Script Management**
   - Upload & Save Script (`/view_script` - POST)
   - View Script in Browser (`/view_script` - GET)
   - Download Script (`/download_script` - GET)
   - Execute Script Automatically (`/run_script` - POST)

4. **Keep Browser Open for Manual Interaction**
   - Ensures that after test execution, the browser remains open for further actions.

5. **Remote Execution & Debugging**
   - Allows users to execute the script remotely and receive execution results.
   - Provides detailed error handling and logging.

## Tech Stack
- Backend: Flask (Python)
- Automation: Selenium WebDriver
- LLM Integration: AWS Bedrock (Titan Model)
- Deployment: Ngrok for public API access

## How to Run the Project

### Install Dependencies
```bash
pip install flask selenium webdriver-manager requests boto3
