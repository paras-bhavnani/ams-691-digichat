# DigiChat: AI-Powered Personalized Nutrition Assistant

DigiChat is a next-generation chatbot designed to deliver precise nutritional insights and health suggestions by leveraging advanced AI models and integrations. It seamlessly integrates with the Nutrition endpoint from API Ninjas, the Edamam Meal Planning API, and a mock FitBit API, providing accurate nutritional data, meal plans, and personalized health recommendations.

## Features
1. **Nutritional Information Retrieval:** Retrieves accurate nutritional data for a wide range of food items using the Nutrition endpoint of API Ninjas.
2. **Personalized Meal Planning:** Generates customized meal plans based on individual dietary needs, preferences, and health goals through the Edamam Meal Planning API.
3. **Activity and Health Tracking:** Incorporates mock FitBit data to provide insights on physical activity, sleep patterns, and overall health metrics.
4. **Health Calculations:** Computes Basal Metabolic Rate (BMR), Total Daily Energy Expenditure (TDEE), Ideal Body Weight (IBW), and more.
5. **Intelligent Recommendations:** Offers personalized health and nutrition advice by analyzing data from multiple sources.
6. **User-Friendly Interaction:** Features a chat-like interface that is easy to use and interact with.

## Setup and Installation

To get DigiChat up and running, follow these steps:

1. **Clone the Repository**

    ```bash
    git clone https://github.com/[YourUsername]/ams-691-digichat.git
    cd DigiChat
    ```

2. **Set Up a Virtual Environment (Optional)**

    It's recommended to create a virtual environment to isolate the dependencies for this project.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    Install the required packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**

    Create a `.env` file in the root directory and add the following keys:

    ```env
    OPENAI_API_KEY=your_openai_api_key
    NUT_API_KEY=your_api_ninjas_key
    EDAMAM_APP_ID=your_edamam_app_id
    EDAMAM_APP_KEY=your_edamam_app_key
    ```

5. **Run the Project**

    You're all set! Run the project with:

    ```bash
    python run_assistant.py
    ```

## Usage

Once the chatbot is running, you can start interacting with it. Here's an example query:

```bash
What is the TDEE of a 30-year-old man, who is 180 cm tall, weighs 80 kg, and exercises 3 times a week?
```

DigiChat will generate a meal plan based on the information provided and also inform the person's BMI.

## Project Structure

### Main Script
- **`run_assistant.py`**: Main script to run the DigiChat assistant.

### Core Functionality
- **`assistant/`**: Directory containing the core assistant functionality.
  - **`health_assistant.py`**: Implements the `HealthAssistant` class.
  - **`fitness_assistant.py`**: Implements the `FitnessAssistant` class with nutrition and fitness-related functions.
  - **`function_parser.py`**: Utility for parsing functions to JSON schema.

### Mock APIs
- **`mock_apis/`**: Directory containing mock API implementations for testing.
  - **`mock_fitbit_api.py`**: Simulates FitBit API for health data.

## License

DigiChat is open-source software licensed under the MIT license.
