# stream-chat-analyzer

This is a chat analysis tool made for YouTube Live Streams.

## Usage

> [!IMPORTANT]
> This part is under construction.

## Data format

The input data is in a CSV format with the following headings.
| Heading | Description |
| :---: | :---: |
| User | The user display name |
| username | the user's actual username on YouTube |
| user_id | The users channel_id on youtube |
| timestamp | The timestamp of when the message happens |
| message | The raw message text |
| profile_url | The user's profile image |

## Ouputs 

The output for this script is
1. Additions to a "master log" that stores every chat message along with what stream it was a part of
2. Graphics produced for each stream
  1. Chat Messages over time
  2. Word Cloud of Common Chat words [^1]
  3. Word Frequency [^1]
  4. Messages per viewer
5. Viewer Profiles - Chat Frequency, Participated Stream, Overall chat Sentiment, Common Words

[^1]: Filler words are filtered out using the NLTK package
