import requests
from datetime import datetime, timedelta
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

# Constants
OPENWEATHER_API_KEY = '*************************'
CALENDARIFIC_API_KEY = '*****************************'
CITY = 'Talegaon Dabhade'
COUNTRY = 'IN'
STATE = 'MH'
SENDINBLUE_API_KEY = '************************************************'
EMAIL_FROM = 'taskreminder@gmail.com'
EMAIL_TO = 'kaushalpawar@gmail.com'

# Helper function to get weather data
def get_weather_forecast():
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY},{COUNTRY}&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data

# Helper function to get holidays
def get_holidays():
    year = datetime.now().year
    url = f"https://calendarific.com/api/v2/holidays?&api_key={CALENDARIFIC_API_KEY}&country={COUNTRY}&year={year}&location={STATE}"
    response = requests.get(url)
    data = response.json()
    holidays = [holiday['date']['iso'] for holiday in data['response']['holidays']]
    return holidays

# Helper function to send email using Sendinblue
def send_email(subject, body):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": EMAIL_TO}],
        sender={"email": EMAIL_FROM},
        subject=subject,
        text_content=body
    )
    
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
        print("Email sent successfully")
    except ApiException as e:
        print(f"Error sending email: {e}")

# Main function
def main():
    weather_data = get_weather_forecast()
    holidays = get_holidays()

    sunny_days = []
    for forecast in weather_data['list']:
        date = forecast['dt_txt'].split(' ')[0]
        weather_main = forecast['weather'][0]['main']
        if weather_main in ['Clear', 'Sunny']:
            sunny_days.append(date)

    today = datetime.now().date()
    next_week = [today + timedelta(days=i) for i in range(7)]
    next_week_dates = [date.strftime('%Y-%m-%d') for date in next_week]

    suitable_days = set(sunny_days) & set(next_week_dates)
    weekend_days = [date.strftime('%Y-%m-%d') for date in next_week if date.weekday() in [5, 6]]
    holiday_days = [date for date in next_week_dates if date in holidays]

    notify_days = set(weekend_days) | set(holiday_days) & suitable_days

    if notify_days:
        subject = "Good Day to Wash Clothes"
        body = f"Upcoming suitable days to wash your clothes: {', '.join(notify_days)}"
        send_email(subject, body)

if __name__ == "__main__":
    main()
