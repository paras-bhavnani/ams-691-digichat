import requests
from assistant.health_assistant import HealthAssistant

class FitnessAssistant:
    def __init__(self, openai_api_key: str, nut_api_key: str, edamam_app_id: str, edmam_app_key: str):
        self.openai_api_key = openai_api_key
        self.nut_api_key = nut_api_key
        self.edamam_app_id = edamam_app_id
        self.edmam_app_key = edmam_app_key
        self.assistant = HealthAssistant(
            openai_api_key=self.openai_api_key,
            custom_functions=[self.get_nutritional_info, self.calculate_bmr, self.calculate_tdee, 
                       self.calculate_ibw, self.calculate_bmi, self.calculate_calories_to_lose_weight, 
                       self.get_meal_plan]
        )

    def get_nutritional_info(self, query: str) -> dict:
        """Fetch the nutritional information for a specific food item.

        :param query: The food item to get nutritional info for
        :return: The nutritional information of the food item
        """
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(query)
        response = requests.get(api_url, timeout=100, headers={'X-Api-Key': self.nut_api_key})

        if response.status_code == requests.codes.ok:
            return response.json()  # Use json instead of text for a more structured data
        else:
            return {"Error": response.status_code, "Message": response.text}
        
    def calculate_bmi(self, weight: float, height: float) -> float:
        """Calculate the Body Mass Index (BMI) for a person.

        :param weight: The weight of the person in kg
        :param height: The height of the person in cm
        :return: The BMI of the person
        """
        height_meters = height / 100  # convert cm to meters
        bmi = weight / (height_meters ** 2)
        return round(bmi, 2)  # round to 2 decimal places for readability
    
    def calculate_calories_to_lose_weight(self, desired_weight_loss_kg: float) -> float:
        """Calculate the number of calories required to lose a certain amount of weight.

        :param desired_weight_loss_kg: The amount of weight the person wants to lose, in kilograms
        :return: The number of calories required to lose that amount of weight
        """
        calories_per_kg_fat = 7700  # Approximate number of calories in a kg of body fat
        return desired_weight_loss_kg * calories_per_kg_fat


    def calculate_bmr(self, weight: float, height: float, age: int, gender: str, equation: str = 'mifflin_st_jeor') -> float:
        """Calculate the Basal Metabolic Rate (BMR) for a person.

        :param weight: The weight of the person in kg.
        :param height: The height of the person in cm.
        :param age: The age of the person in years.
        :param gender: The gender of the person ('male' or 'female')
        :param equation: The equation to use for BMR calculation ('harris_benedict' or 'mifflin_st_jeor')
        :return: The BMR of the person
        """
        if equation.lower() == 'mifflin_st_jeor':
            if gender.lower() == 'male':
                return (10 * weight) + (6.25 * height) - (5 * age) + 5
            else:  # 'female'
                return (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:  # 'harris_benedict'
            if gender.lower() == 'male':
                return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:  # 'female'
                return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Calculate the Total Daily Energy Expenditure (TDEE) for a person.

        :param bmr: The BMR of the person
        :param activity_level: The activity level of the person
        ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'super_active')
        :return: The TDEE of the person
        """
        activity_factors = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'super_active': 1.9,
        }
        return bmr * activity_factors.get(activity_level, 1)

    def calculate_ibw(self, height: float, gender: str) -> float:
        """Calculate the Ideal Body Weight (IBW).

        :param height: The height of the person in inches
        :param gender: The gender of the person ("male" or "female")
        :return: The Ideal Body Weight in kg
        """
        if gender.lower() == 'male':
            if height <= 60:  # 5 feet = 60 inches
                return 50
            else:
                return 50 + 2.3 * (height - 60)
        elif gender.lower() == 'female':
            if height <= 60:
                return 45.5
            else:
                return 45.5 + 2.3 * (height - 60)
        else:
            raise ValueError("Invalid gender. Expected 'male' or 'female'.")
        
    def handle_user_activity_data(self, user_id: str, date: str) -> str:
        """Process and return user activity data

        :param user_id: The unique identifier for the user
        :param date: The date for which to fetch smartwatch data
        :return: A summary of the user's smartwatch data for the specified date
        """
        activity_data = self.get_fitbit_data(user_id, date, 'activities')
        sleep_data = self.get_fitbit_data(user_id, date, 'sleep')
        heart_rate_data = self.get_fitbit_data(user_id, date, 'heart')
        
        summary = f"On {date}:\n"
        summary += f"- Steps: {activity_data.get('TotalSteps', 'N/A')}\n"
        summary += f"- Sleep: {sleep_data.get('totalMinutesAsleep', 'N/A')} minutes\n"
        summary += f"- Resting Heart Rate: {heart_rate_data.get('restingHeartRate', 'N/A')} bpm"
        
        return summary

    def get_fitbit_data(self, user_id: str, date: str, data_type: str) -> dict:
        """Fetch Fitbit data from the mock API.

        :param user_id: The unique identifier for the user
        :param date: The date for which to fetch data
        :param data_type: The type of data to fetch (activities, sleep, or heart)
        :return: A dictionary containing the requested Fitbit data, or None if the request fails
        """
        base_url = 'http://localhost:5000/api/user'
        url = f'{base_url}/{user_id}/{data_type}/date/{date}'
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # logging.error(f"Error fetching Fitbit data: {e}")
            return None
        
    def get_meal_plan(self, calories: int, diet: str = None, health: str = None) -> dict:
        """
        Fetch a personalized meal plan based on user requirements.
        
        :param calories: Daily calorie goal
        :param diet: Optional diet type (e.g., 'balanced', 'low-fat', 'low-carb')
        :param health: Optional health label (e.g., 'vegan', 'vegetarian', 'peanut-free')
        :return: A dictionary containing the meal plan
        """
        base_url = 'https://api.edamam.com/api/meal-planner/v1'
        params = {
            'app_id': self.edamam_app_id,
            'app_key': self.edmam_app_key,
            'calories': calories,
            'diet': diet,
            'health': health
        }
        
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"Error": response.status_code, "Message": response.text}
        
    def ask(self, question: str):
        response = self.assistant.ask(question)
        return response

    def view_functions(self):
        return self.assistant.functions

    def view_chat_history(self):
        return self.assistant.chat_history