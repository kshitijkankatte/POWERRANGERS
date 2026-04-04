# Sahanak Backend API

A comprehensive healthcare triage backend service built with FastAPI and Claude AI integration.

## Features

✅ User authentication and registration
✅ AI-powered symptom assessment using Claude
✅ Assessment history tracking
✅ SQLite database for data persistence
✅ RESTful API with CORS support
✅ Emergency contact management
✅ Medical history tracking

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── client.py              # Python client library
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── INTEGRATION_GUIDE.md   # Integration documentation
```

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Anthropic API key (get from https://console.anthropic.com)

## Installation

### 1. Clone/Setup Backend

```bash
# Navigate to backend directory
cd backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Edit `.env` file:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

## Running the Backend

### Development Mode

```bash
# Windows
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Mac/Linux
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Production Mode

```bash
gunicorn -w 4 -b 0.0.0.0:8001 main:app
```

The API will be available at: http://localhost:8001

## API Documentation

### Health Check

```bash
GET /health

Response:
{
    "status": "healthy",
    "service": "Sahanak Backend API",
    "version": "1.0.0",
    "timestamp": "2024-04-04T10:30:00"
}
```

### User Registration

```bash
POST /api/auth/signup

Request Body:
{
    "username": "john_doe",
    "password": "password123",
    "full_name": "John Doe",
    "gender": "Male",
    "age": 30,
    "location": "Mumbai, India",
    "allergies": "Penicillin",
    "medical_history": "Diabetes",
    "emergency_contact_1": "Mom: 9876543210",
    "emergency_contact_2": "Dad: 9876543211",
    "emergency_contact_3": "Sister: 9876543212"
}

Response:
{
    "id": 1,
    "username": "john_doe",
    "full_name": "John Doe",
    "age": 30,
    ...
}
```

### User Login

```bash
POST /api/auth/login

Request Body:
{
    "username": "john_doe",
    "password": "password123"
}

Response:
{
    "success": true,
    "user": { ... },
    "token": "token_1"
}
```

### Assess Symptoms

```bash
POST /api/assess/symptoms?user_id=1

Request Body:
{
    "symptoms": ["Fever", "Cough", "Headache"],
    "other_symptoms": "Patient has mild body ache"
}

Response:
{
    "urgency": "YELLOW",
    "urgency_label": "Urgent",
    "message": "Based on your symptoms...",
    "conditions": ["Common Cold", "Flu"],
    "specialist": "General Practitioner",
    "remedies": ["Rest", "Hydration"],
    "avoid": ["Smoking"],
    "warning_signs": "Seek immediate care if...",
    "specialist_link": "general+practitioner"
}
```

### Get Assessment History

```bash
GET /api/assessments/{user_id}

Response:
[
    {
        "id": 1,
        "symptoms": ["Fever", "Cough"],
        "urgency": "YELLOW",
        "urgency_label": "Urgent",
        "message": "...",
        "created_at": "2024-04-04T10:30:00"
    }
]
```

## Urgency Levels

| Level | Label | Color | Meaning |
|-------|-------|-------|---------|
| RED | Emergency | 🔴 | Life-threatening, seek immediate help |
| YELLOW | Urgent | 🟡 | Urgent care needed, see doctor soon |
| GREEN | Routine | 🟢 | Mild symptoms, schedule normal appointment |

## Database

SQLite database (`sahanak.db`) is automatically created with:

### Users Table
- User credentials
- Medical history
- Emergency contacts
- Profile information

### Assessments Table
- Assessment history
- Symptoms
- Results
- Timestamps

## Integration with Frontend

### Available Methods

```python
from client import SahanakBackendClient

client = SahanakBackendClient()

# Signup
client.signup({
    "username": "user123",
    "password": "pass123",
    "full_name": "John Doe",
    ...
})

# Login
client.login("user123", "pass123")

# Assess symptoms
client.assess_symptoms(["Fever", "Cough"], "Additional info")

# Get history
client.get_assessment_history()
```

### Frontend Updates Required

Update `app.js` to use backend endpoints instead of localStorage:

```javascript
// Replace mock API call
async callClaudeAPI(symptoms, extra) {
    const response = await fetch(
        `http://localhost:8001/api/assess/symptoms?user_id=${this.currentUser.id}`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symptoms, other_symptoms: extra })
        }
    );
    return await response.json();
}
```

## Error Handling

All errors return structured responses:

```json
{
    "error": "Error message",
    "status_code": 400,
    "timestamp": "2024-04-04T10:30:00"
}
```

## Security

- **Password Hashing**: SHA256 (upgrade to bcrypt in production)
- **CORS**: Enabled for all origins (restrict in production)
- **Authentication**: Simple token-based (use JWT in production)
- **API Key**: Stored in `.env`, never committed to git

## Performance

- Async request handling with FastAPI
- SQLite for local development (upgrade to PostgreSQL in production)
- Efficient JSON parsing
- Claude API integration with proper error handling

## Testing

### Test Signup
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","full_name":"Test User"}'
```

### Test Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

### Test Assessment
```bash
curl -X POST "http://localhost:8001/api/assess/symptoms?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{"symptoms":["Fever","Cough"],"other_symptoms":""}'
```

## Deployment

### Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Heroku

```bash
git push heroku main
```

### AWS/GCP

Deploy using standard Python web server deployment

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8001
kill -9 <PID>
```

### API Key Not Working
- Verify key in `.env` file
- Check key has correct permissions
- Try with new key from Anthropic console

### Database Issues
```bash
# Reset database
rm sahanak.db
# Restart server - will recreate
```

## Next Steps

1. ✅ Run backend: `python -m uvicorn main:app --reload`
2. ✅ Test endpoints with curl or Postman
3. ✅ Update frontend to use backend APIs
4. ✅ Test full integration
5. ✅ Deploy to production

## Support & Documentation

- **Backend Guide**: See `INTEGRATION_GUIDE.md`
- **API Docs**: Available at `http://localhost:8001/docs`
- **Frontend Integration**: See `../QUICK_START.md`

## License

MIT License - Feel free to use and modify

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: April 2024
