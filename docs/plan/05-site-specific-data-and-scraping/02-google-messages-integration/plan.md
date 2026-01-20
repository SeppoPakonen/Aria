# Phase 02: Google Messages Integration

## Tasks
1. **01-google-messages-navigation**: Implement logic to navigate to Google Messages and detect the active conversation list.
2. **02-conversation-crawler**: Implement a loop to visit each conversation and extract message history.
3. **03-media-downloader**: Implement detection and downloading of images, videos, and audio files from messages.
4. **04-implement-show-recent**: Implement `aria site google-messages show recent` to display the latest local data.

## Supported URLs
- https://messages.google.com/web/conversations

## Completion Criteria
- User can run `aria site google-messages refresh` to sync all data.
- User can run `aria site google-messages show recent` to see messages without opening the browser.
