# Free Fire Bot Services

## Overview
Premium Free Fire Bot Services website with VIP features including player information lookup, dance emotes, and ghost attacks.

## Project Info
- **Developed by**: SK7 D5M AND H4RDIXX official
- **Port**: 5000 (Flask web server)
- **Framework**: Python Flask

## Recent Changes
- December 16, 2025: Redesigned info response display with beautiful player cards
- December 16, 2025: Added developer credits (SK7 D5M AND H4RDIXX official)
- December 16, 2025: Updated UI with professional dark theme styling
- December 16, 2025: Added Player Information Lookup section on homepage

## Project Structure
```
/
├── main.py              # Main Flask application
├── lib2.py              # API library for Free Fire data
├── static/
│   ├── index.html       # Homepage
│   ├── style.css        # Styling
│   ├── script.js        # JavaScript functionality
│   ├── login.html       # VIP login page
│   ├── vip.html         # VIP dashboard
│   └── admin.html       # Admin panel
├── emotes_data.json     # Dance emotes data
├── stats_data.json      # Website statistics
└── vip_users.json       # VIP users data
```

## Features
1. **Player Information Lookup** - Beautiful card display with all player stats
2. **VIP Dashboard** - Access dance and ghost features
3. **Statistics** - Track website visits and bot usage
4. **Dance Emotes** - Display available emotes with icons

## Running the Project
The project runs on port 5000 with: `python main.py`
