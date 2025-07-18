import re
import pandas as pd

def preprocess(data):
    # Updated pattern to match the actual WhatsApp format: M/D/YY, H:MM AM/PM -
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s[AP]M\s-\s'

    # Split the data into messages based on the pattern
    messages = re.split(pattern, data)[1:]  # Remove the empty string at the beginning

    # Find all dates
    dates = re.findall(pattern, data)

    # Ensure we have matching messages and dates
    if len(messages) != len(dates):
        # If lengths don't match, take the minimum to avoid errors
        min_len = min(len(messages), len(dates))
        messages = messages[:min_len]
        dates = dates[:min_len]

    # Create DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date type - updated format to match M/D/YY, H:MM AM/PM -
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p - ')

    users = []
    processed_messages = []
    for message in df['user_message']:
        # Clean the message by removing extra whitespace and newlines
        message = message.strip()
        # Split by the first colon to separate user and message
        entry = re.split('([\w\W]+?):\s', message, maxsplit=1)
        if len(entry) >= 3 and entry[1]:  # user name exists
            users.append(entry[1])
            processed_messages.append(" ".join(entry[2:]).replace('\n', ' ').strip())
        else:
            users.append('group_notification')
            processed_messages.append(message.replace('\n', ' ').strip())

    df['user'] = users
    df['message'] = processed_messages
    df['only_date'] = df['message_date'].dt.date
    df['year'] = df['message_date'].dt.year
    df['month_num'] = df['message_date'].dt.month
    df['month'] = df['message_date'].dt.month_name()
    df['day'] = df['message_date'].dt.day
    df['day_name'] = df['message_date'].dt.day_name()
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute

    # Add period column
    df = add_period_column(df)

    return df

def add_period_column(df):
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period
    return df

