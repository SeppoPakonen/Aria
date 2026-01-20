# Phase 03: WhatsApp & Discord Integration

## Tasks
1. **[DONE] 01-whatsapp-navigation-and-scraping**: Implement WhatsApp scraper with synthetic clicks and timestamp extraction.
2. **02-discord-navigation-and-scraping**: Implement `DiscordScraper` to handle server/channel navigation and message extraction.
3. **03-discord-persistent-ids**: Integrate Discord with `SiteManager` registry for stable server/channel numbering.

## Supported URLs
- https://web.whatsapp.com/
- https://discord.com/app

## Completion Criteria
- User can run `aria site refresh discord` to sync all visible DMs and channel history.
- User can run `aria site show discord list` to see a numbered list of Discord servers/channels.
- User can run `aria site show discord <id> show` to view chat history.
