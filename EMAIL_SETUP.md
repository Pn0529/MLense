# Email Configuration Guide for ExamBridge

## Required Environment Variables

Add these to your `.env` file or system environment:

### Option 1: Gmail (Recommended)
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Note**: For Gmail, you need an "App Password" not your regular password:
1. Go to Google Account → Security → 2-Step Verification → App passwords
2. Generate app password for "Mail"
3. Use that 16-character password

### Option 2: Other Email Providers

**Outlook/Hotmail:**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
```

**Yahoo:**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SENDER_EMAIL=your-email@yahoo.com
SENDER_PASSWORD=your-app-password
```

### Option 3: Disable Email (Development)
If you don't need emails in development, the system will log a warning and skip sending.

## Testing Email

Once configured, restart the backend server and try clicking "I'm Done" after completing a quiz.

## Troubleshooting

1. **"Failed to send email"** - Check SENDER_PASSWORD is set correctly
2. **Authentication errors** - Use App Password for Gmail, not regular password
3. **Connection errors** - Check SMTP_SERVER and SMTP_PORT values
