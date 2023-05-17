#Функция для получения времени от пользователя
def get_time_user(message):
    month_data, time_data = message.split(' ')
    day = month_data.split('.')[0]
    month = month_data.split('.')[1]
    hour = time_data.split(':')[0]
    minute = time_data.split(':')[1]
    return day,month,hour,minute
