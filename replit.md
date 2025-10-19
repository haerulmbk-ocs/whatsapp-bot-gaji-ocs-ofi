# WhatsApp Bot Gaji OCS OFI

## Overview
A Flask-based WhatsApp bot for calculating Indonesian salary and overtime payments. The bot automatically calculates total income per payment period with BPJS and tax considerations.

## Project Information
- **Language**: Python 3.11
- **Framework**: Flask 2.3.3
- **Web Server**: Gunicorn 20.1.0
- **Port**: 5000
- **Type**: Webhook-based REST API

## Features
1. **Overtime Calculator** - Calculates overtime pay according to Indonesian labor regulations
2. **Salary Slip Generator** - Creates detailed salary slips including BPJS contributions and taxes
3. **Help System** - Interactive help commands in Bahasa Indonesia

## Project Structure
- `app.py` - Main Flask application with webhook endpoints and calculation logic
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification
- `Procfile` - Deployment configuration (Heroku-style)

## API Endpoints
- `GET /webhook` - Health check endpoint
- `POST /webhook` - Main webhook endpoint for processing WhatsApp messages

## Bot Commands
1. `hitung lembur [gaji] [jam]` - Calculate overtime
2. `slip gaji [gaji] [lembur] [potongan]` - Generate salary slip
3. `help` or `bantuan` - Show help menu

## Recent Changes
- **2025-10-19**: Initial import and Replit environment setup
  - Installed Python 3.11 with Flask and Gunicorn
  - Created .gitignore for Python projects
  - Configured workflow to run on port 5000
