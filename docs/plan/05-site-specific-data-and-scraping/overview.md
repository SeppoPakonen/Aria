# Track 05: Site-Specific Data & Scraping

## Objective
Implement a robust framework for site-tailored automation and personal data scraping. This track focuses on gathering data from specific platforms (Messages, WhatsApp, Calendar, etc.) and storing it in a structured local JSON-based database for offline querying and indexing.

## Core Concepts
- **Site Manager**: A new component to handle site-specific logic and routing.
- **Local JSON Database**: Data stored in `~/.aria/sites/{site_name}/` using JSON files for messages, events, and metadata.
- **Media Indexing**: Local storage and indexing of images, videos, and audio files downloaded during scraping.
- **Site CLI**: `aria site <site_name> <command>` interface.

## Phases

| ID | Name                                      | Objective                                                                     | Status      |
|----|-------------------------------------------|-------------------------------------------------------------------------------|-------------|
| 01 | Data Architecture & Framework             | Implement `SiteManager`, local storage logic, and the `site` command base.    | Planned     |
| 02 | Google Messages Integration               | Implement full scraping (conversations, media) and local query commands.      | Planned     |
| 03 | WhatsApp & Discord Integration            | Implement scraping logic for WhatsApp and Discord.                            | In Progress |
| 04 | Threads, Calendar & YouTube Studio        | Implement scraping for Threads, Google Calendar, and YouTube Studio.          | Planned     |
| 05 | Sync & Maintenance                        | Implement incremental refreshes, data integrity checks, and maintenance.      | Planned     |

## Runbook Alignment
This track introduces the `aria site` command family, which will eventually be documented in a new runbook `60-sites-and-data.md`.
