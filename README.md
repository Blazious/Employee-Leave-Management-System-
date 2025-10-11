# Enterprise Leave Management System (ELMS)

A comprehensive Django-based leave management system designed for modern organizations. This system provides a complete solution for managing employee leave requests, approvals, and notifications with professional document generation.

## 🚀 Features

### Core Functionality
- **Employee Leave Requests**: Submit and track leave applications
- **Multi-level Approval Workflow**: HOD and HR approval hierarchy
- **Leave Balance Management**: Track remaining leave days per employee
- **Professional PDF Generation**: Automated leave request documents with company branding
- **Email Notifications**: Automated emails with PDF attachments for approvals
- **Holiday Exclusion**: Smart calculation excluding weekends and public holidays

### Advanced Features
- **JWT Authentication**: Secure API access with token-based authentication
- **RESTful API**: Complete API endpoints for frontend integration
- **Audit Logging**: Track all leave request activities
- **Professional Styling**: Corporate-grade PDF documents with privacy statements
- **Kenya Public Holidays**: Built-in holiday calendar with automatic calculation

## 📋 System Requirements

- Python 3.8+
- Django 5.2+
- PostgreSQL/SQLite (SQLite for development)
- Email service (SMTP configuration required for notifications)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd ELMS
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the `leave_management` directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 5. Database Setup
```bash
cd leave_management
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## 🔧 API Endpoints

### Authentication
- `POST /api/users/api/token/` - Obtain JWT token
- `POST /api/users/api/token/refresh/` - Refresh JWT token
- `POST /api/users/api/token/verify/` - Verify JWT token

### Leave Management
- `GET /api/leave/leave-types/` - List all leave types
- `POST /api/leave/leave-requests/` - Create new leave request
- `GET /api/leave/leave-requests/` - List leave requests
- `POST /api/leave/leave-requests/{id}/approve/` - Approve leave request
- `POST /api/leave/leave-requests/{id}/reject/` - Reject leave request
- `GET /api/leave/leave-requests/{id}/download_pdf/` - Download leave PDF
- `GET /api/leave/leave-balances/` - Get leave balances

### Testing & Utilities
- `GET /api/leave/test-holidays/` - Test holiday calculations

## 👥 User Roles

### Employee
- Submit leave requests
- View own leave history
- Download approved leave documents

### HOD (Head of Department)
- View department leave requests
- Provide initial approval/rejection
- Add comments to requests

### HR (Human Resources)
- Final approval authority
- View all leave requests
- Manage leave balances
- Generate reports

## 📧 Email System

The system automatically sends email notifications:

### For Approved Leave:
- Professional HTML email with all leave details
- PDF attachment with official leave document
- Includes privacy statements and legal disclaimers

### For Rejected Leave:
- Notification email with rejection reason
- Manager comments included

## 📄 Professional PDF Documents

Generated leave documents include:
- **Company Branding**: Professional header and footer
- **Employee Information**: Complete employee details
- **Leave Details**: Dates, type, working days calculation
- **Approval Information**: Approver details and timestamps
- **Privacy Statements**: Legal disclaimers and confidentiality notices
- **Document Authentication**: Unique document IDs and timestamps

## 🏖️ Holiday Management

The system automatically excludes:
- **Weekends**: Saturdays and Sundays
- **Kenya Public Holidays**:
  - New Year's Day
  - Labour Day
  - Madaraka Day
  - Mashujaa Day
  - Jamhuri Day
  - Christmas Day
  - Boxing Day
  - Good Friday
  - Easter Monday

## 🔒 Security Features

- JWT-based authentication
- Role-based access control
- Input validation and sanitization
- Secure file handling
- Environment variable protection

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Specific test categories:
```bash
# Test holiday calculations
python manage.py test leave.tests.HolidayTests

# Test all leave functionality
python manage.py test leave.tests
```

## 📱 API Usage Examples

### Create Leave Request
```bash
curl -X POST http://localhost:8000/api/leave/leave-requests/ \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "leave_type": 1,
    "start_date": "2025-10-09",
    "end_date": "2025-10-22",
    "reason": "Family vacation"
  }'
```

### Approve Leave Request
```bash
curl -X POST http://localhost:8000/api/leave/leave-requests/1/approve/ \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"comments": "Approved for family time"}'
```

## 🚀 Deployment

### Production Settings
1. Set `DEBUG=False` in environment variables
2. Configure production database (PostgreSQL recommended)
3. Set up proper email service (SendGrid, AWS SES, etc.)
4. Configure static file serving
5. Set up SSL certificates
6. Configure reverse proxy (Nginx)

### Docker Deployment (Optional)
```dockerfile
# Add Dockerfile and docker-compose.yml for containerized deployment
```

## 📊 Project Structure

```
ELMS/
├── leave_management/          # Main Django project
│   ├── leave/                # Leave management app
│   │   ├── models.py         # Data models
│   │   ├── views.py          # API views
│   │   ├── serializers.py    # Data serialization
│   │   ├── utils/            # Utility functions
│   │   └── templates/        # Email templates
│   ├── user/                 # User management app
│   ├── audit/                # Audit logging app
│   └── templates/            # Global templates
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🎯 Roadmap

- [ ] Mobile app integration
- [ ] Advanced reporting dashboard
- [ ] Integration with HR systems
- [ ] Multi-language support
- [ ] Advanced approval workflows
- [ ] Calendar integration

---

**Enterprise Leave Management System** - Streamlining leave management for modern organizations.
