# Elegant Flask Application

A Flask web application for Elegant - A simple approach to the immigration process. Your gateway to a better future.

## Setup Instructions

### 1. Install Python Dependencies

First, install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Run the Application

Start the Flask development server:

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

### 3. Available Routes

- **Home Page**: `http://localhost:5000/`
- **Services**: `http://localhost:5000/services`
- **Pricing**: `http://localhost:5000/pricing`
- **About**: `http://localhost:5000/about`
- **Contact**: `http://localhost:5000/contact`

### 4. API Endpoints

- **Contact Form Submission**: `POST /api/contact`
  - Accepts JSON data with fields: name, email, company, subject, message
  - Returns success/error response

## Project Structure

```
2142_cloud_sync/
├── app.py                          # Flask application with routes
├── requirements.txt                # Python dependencies
├── templates/                      # HTML templates
│   └── index.html                 # Main page template
├── static/                         # Static files (CSS, JS, images)
│   ├── tooplate-cloud-sync-style.css
│   ├── tooplate-cloud-scripts.js
│   └── images/
│       ├── tooplate-cloud-sync-bg01.jpg
│       ├── tooplate-cloud-sync-bg02.jpg
│       └── tooplate-cloud-sync-bg03.jpg
└── README.md                       # This file
```

## Development

- The application runs in debug mode by default for development
- Debug mode enables auto-reload when you make changes to the code
- Access the app from any device on your network using your local IP address

## Production Deployment

For production deployment, consider:
- Setting `debug=False` in app.py
- Using a production WSGI server like Gunicorn or uWSGI
- Setting up environment variables for configuration
- Implementing proper logging and error handling
- Adding database integration for contact form submissions

## Features

- Immigration services website with elegant red, white, and black theme
- Multi-route support for different sections (Services, Pricing, About, Contact)
- Contact form API endpoint for consultation requests
- Static file serving for CSS, JS, and images
- Error handling (404, 500)
- Responsive design
- Modern UI with animations
- Professional immigration service presentation

## Credits

- Company Name: Elegant
- Template Design: Tooplate
- Flask Framework: Pallets Projects

