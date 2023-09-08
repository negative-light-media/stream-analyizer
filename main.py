import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
from textblob import TextBlob
import os
import shutil
import argparse
import csv
from datetime import datetime
import yaml
from nltk.corpus import stopwords
from nltk import download

download('stopwords')

def sanitizeFileName(original: str):
    return original.replace(" ", "_").replace("/", "_").replace('?', "_").replace('!', "_")

def generate_filename(stream_title, plot_type):
    date_str = datetime.now().strftime("%Y%m%d")
    stream_title_sanitized = sanitizeFileName(stream_title) # Replace spaces and slashes with underscores
    filename = f"{date_str}-{stream_title_sanitized}-{plot_type}.png"
    return filename

def load_data(file_path):
    data = pd.read_csv(file_path, on_bad_lines='skip')
    print(data)
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    return data

def message_type(message):
    if message.endswith('?'):
        return 'Question'
    return 'Statement'

def sentiment_analysis(message):
    blob = TextBlob(message)
    return blob.sentiment.polarity

def summary_statistics(data):
    return data['user'].value_counts().head(5), data['user'].nunique()

def timestamp_analysis(data, stream_title):
    message_frequency = data.resample('1Min', on='timestamp').size()
    plt.plot(message_frequency, marker='o', linestyle='-')
    plt.title('Frequency of Messages Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Number of Messages')
    plt.grid(True)
    plot_type = "message_frequency"
    filename = generate_filename(stream_title, plot_type)
    plt.savefig(filename)
    plt.close()

def common_words_analysis(data, stream_title):
    words = ' '.join(data['filtered_message'].dropna()).split()
    word_counts = Counter(words)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counts)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title('Most Common Words in Chat Messages')
    plot_type = "word_plot"
    filename = generate_filename(stream_title, plot_type)
    plt.savefig(filename)
    plt.close()

def user_profiles(data):
    profiles = {}
    for user in data['user'].unique():
        user_data = data[data['user'] == user]
        messages = user_data['message'].dropna()
        message_types = [message_type(msg) for msg in messages]
        sentiments = [sentiment_analysis(msg) for msg in messages]
        profiles[user] = {
            'total_messages': len(user_data),
            'common_words': Counter(' '.join(messages).split()).most_common(5),
            'sample_messages': messages.sample(min(3, len(user_data))).tolist(),
            'message_types': Counter(message_types),
            'average_sentiment': sum(sentiments) / len(sentiments) if sentiments else 0
        }
    return profiles

def analyze_stream(file_path, stream_title):
    # Load in the data
    data = load_data(file_path)
    # Remove Stop Words
    with open("./filter_words.yaml", "r") as file:
        words = yaml.safe_load(file)
    stop = stopwords.words('english')
    data['filtered_message'] = data['message'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    print(data.head())
    summary_statistics(data)
    timestamp_analysis(data, stream_title)
    common_words_analysis(data, stream_title)
    profiles = user_profiles(data)

    # Copying the CSV file with the specified format
    date_str = data['timestamp'].dt.strftime('%y%m%d').iloc[0]
    new_file_path = f"{date_str}-{sanitizeFileName(stream_title)}.csv"
    shutil.copy(file_path, new_file_path)

    # Adding the stream title as a column and appending to master-log.csv
    data['stream_title'] = stream_title
    master_log_path = "master-log.csv"
    data.to_csv(master_log_path, mode='a', header=not os.path.exists(master_log_path), index=False)

    return profiles

def clear_chat_log(file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze YouTube livestream chat log.")
    parser.add_argument("file_path", nargs='?', default="./chat-log.csv", help="Path to the CSV file containing the chat log. Defaults to ./chat-log.csv.")
    parser.add_argument("stream_title", help="Title of the stream.")
    args = parser.parse_args()

    analyze_stream(args.file_path, args.stream_title)
    print("Analysis complete.")
    print("Clearing Stream Data for Base Log")
    headers = ["user", "username", "user_id", "message_id", "timestamp", "message", "profile_url"]
    clear_chat_log(args.file_path)

