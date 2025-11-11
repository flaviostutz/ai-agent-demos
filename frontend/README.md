# Loan Application Frontend

A modern React.js web application for submitting loan applications with AI-powered instant evaluation.

## Features

- **Comprehensive Form**: Collects all required information for loan evaluation
  - Personal Information
  - Employment Details
  - Financial Information
  - Credit History
  - Loan Details

- **Real-time Validation**: Client-side validation with helpful error messages
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **AI-Powered Evaluation**: Instant loan decisions using the AI agent backend
- **Beautiful UI**: Modern gradient design with smooth animations

## Prerequisites

- Node.js (v18 or higher)
- pnpm (Fast, disk space efficient package manager)
- Running loan approval API backend (default: http://localhost:8000)

## Installation

```bash
# Install pnpm if not already installed
npm install -g pnpm

# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install
```

## Running the Application

### Development Mode

```bash
pnpm run dev
```

The application will start at `http://localhost:3000`

### Production Build

```bash
# Build for production
pnpm run build

# Preview production build
pnpm run preview
```

## Configuration

Create a `.env` file in the frontend directory to configure the API endpoint:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Usage

1. **Start the Backend API**: Make sure the loan approval API is running on port 8000
   ```bash
   cd ..
   make run
   ```

2. **Start the Frontend**: In a new terminal
   ```bash
   cd frontend
   pnpm run dev
   ```

3. **Access the Application**: Open `http://localhost:3000` in your browser

4. **Fill the Form**: 
   - Enter all required fields (marked with *)
   - Use the sample data format:
     - SSN: XXX-XX-XXXX (e.g., 123-45-6789)
     - Phone: +1XXXXXXXXXX (e.g., +15551234567)
     - State: Two letter code (e.g., NY)
     - Credit Score: 300-850

5. **Submit**: Click "Submit Application" to receive instant AI-powered evaluation

## Form Sections

### Personal Information
- Name, Date of Birth, SSN
- Contact details (Email, Phone)
- Address information

### Employment Information
- Employment status and details
- Income information
- Industry details

### Financial Information
- Monthly debt payments
- Bank account balances
- Asset reserves
- Bankruptcy/foreclosure history

### Credit History
- Credit score
- Credit cards and utilization
- Payment history
- Credit inquiries

### Loan Details
- Loan amount and purpose
- Loan term
- Property details (for home loans)

## API Integration

The application integrates with the loan approval API:

- **Endpoint**: `POST /api/v1/loan/evaluate`
- **Response**: Loan decision with reasoning and recommendations
- **Health Check**: `GET /health`

## Development

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── LoanApplicationForm.jsx  # Main form component
│   ├── api.js                        # API client
│   ├── App.jsx                       # Root component
│   ├── App.css                       # App styles
│   ├── index.css                     # Global styles
│   └── main.jsx                      # Entry point
├── index.html                        # HTML template
├── vite.config.js                    # Vite configuration
└── package.json                      # Dependencies
```

### Technologies Used

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client for API requests
- **CSS3**: Modern styling with gradients and animations

## Troubleshooting

### API Connection Issues

If you get network errors:
1. Ensure the backend API is running on port 8000
2. Check CORS settings are enabled in the API
3. Verify the API_BASE_URL in your `.env` file

### Form Validation Errors

- SSN must be in format XXX-XX-XXXX
- Email must be valid format
- State must be 2 letters
- Credit score must be between 300-850
- All required fields must be filled

## License

See LICENSE file in the root directory.
