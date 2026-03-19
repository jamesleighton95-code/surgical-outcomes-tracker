# Surgical Outcomes Tracker

A professional platform for consultants to log theatre cases (without patient identifiable information) and track surgical outcomes. Built with Python Azure Functions backend and vanilla JavaScript frontend, hosted on Azure.

## Features

- **Secure Case Logging**: Record theatre cases without patient identifiable information
- **Outcome Tracking**: Monitor procedure outcomes, complications, and success rates
- **Analytics Dashboard**: View statistics and trends in your surgical practice
- **Custom Queries**: Ask questions about your data in plain English (AI-powered)
- **Data Export**: Export case data for further analysis
- **Azure Integration**: Secure, HIPAA-compliant cloud infrastructure

## Tech Stack

### Backend
- **Python 3.11** with Azure Functions
- **Azure SQL Database** for data storage
- **Azure Blob Storage** for file attachments
- **JWT Authentication** with bcrypt password hashing
- **OpenAI API** for custom query processing (optional)

### Frontend
- **Vanilla HTML/CSS/JavaScript** (no framework required)
- **Azure Static Web Apps** for hosting
- **Progressive Web App** capabilities

## Project Structure

```
surgical-outcomes-tracker/
├── api-python/                 # Python Azure Functions backend
│   ├── function_app.py        # Main API routes
│   ├── shared/                # Shared utilities
│   │   ├── auth.py           # JWT authentication
│   │   ├── database.py       # Database queries
│   │   └── storage.py        # Azure Blob Storage
│   ├── schema.sql            # Database schema
│   ├── requirements.txt      # Python dependencies
│   └── host.json            # Azure Functions config
│
├── build/www/                 # Frontend files
│   ├── index.html           # Landing page
│   ├── login.html           # Login page
│   ├── signup.html          # Registration page
│   ├── dashboard.html       # Main dashboard
│   ├── config.js            # API configuration
│   └── styles.css           # Styling
│
├── .github/workflows/         # CI/CD pipeline
│   └── azure-deploy.yml      # GitHub Actions workflow
│
├── .env                       # Environment variables (not committed)
├── .gitignore                # Git ignore rules
├── package.json              # NPM scripts
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Azure account with active subscription
- Azure Functions Core Tools v4
- Git
- Node.js (for npm scripts)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd surgical-outcomes-tracker
   ```

2. **Set up environment variables**
   ```bash
   cp .env .env.local
   # Edit .env.local with your Azure credentials
   ```

3. **Install Python dependencies**
   ```bash
   cd api-python
   pip install -r requirements.txt
   ```

4. **Start the development servers**
   ```bash
   # From the root directory
   npm start
   ```

   This will start:
   - Frontend on http://localhost:5001
   - API on http://localhost:7071

5. **Set up the database**
   - Create an Azure SQL Database
   - Run the schema.sql script in Azure Portal Query Editor
   - Update .env.local with database credentials

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Database Schema

The database includes the following main tables:

- **Users**: Consultant accounts
- **Cases**: Theatre case records
- **CustomMetrics**: Procedure-specific metrics
- **Outcomes**: Detailed outcome tracking
- **Attachments**: File attachments (stored in Azure Blob Storage)
- **SavedQueries**: User's saved queries
- **AuditLog**: Change tracking

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Cases
- `GET /api/cases` - Get all cases for user
- `POST /api/cases` - Create new case
- `GET /api/cases/{caseId}` - Get specific case
- `PUT /api/cases/{caseId}` - Update case
- `DELETE /api/cases/{caseId}` - Delete case

### Analytics
- `GET /api/statistics` - Get case statistics
- `POST /api/query` - Custom AI-powered query

### User
- `GET /api/profile` - Get user profile

## Security

- All endpoints except authentication require JWT token
- Passwords are hashed using bcrypt
- Database credentials stored in Azure Key Vault (production)
- HTTPS enforced on all connections
- CORS configured for allowed origins only

## Environment Variables

Required environment variables (see `.env` file):

```bash
# Azure
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id

# Database
DB_SERVER=your-server.database.windows.net
DB_NAME=surgical-outcomes-db
DB_USER=dbadmin
DB_PASSWORD=your-password

# Authentication
JWT_SECRET=your-secret-key

# Storage
AZURE_STORAGE_CONNECTION_STRING=your-connection-string

# Optional
OPENAI_API_KEY=your-openai-key
```

## Contributing

This is a private project. For questions or issues, contact the project maintainer.

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
1. Check the DEPLOYMENT.md guide
2. Review Azure Function logs in Application Insights
3. Check browser console for frontend errors

## Roadmap

- [ ] Mobile app (Capacitor wrapper)
- [ ] Advanced analytics with charts
- [ ] AI-powered outcome prediction
- [ ] Multi-language support
- [ ] Export to PDF/Excel
- [ ] Team collaboration features
