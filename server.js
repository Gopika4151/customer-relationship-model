const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const cors = require('cors');

const app = express();

// Security Headers
app.use(helmet());

// CORS Policy
app.use(cors({
  origin: 'http://localhost:5173',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true
}));

app.use(express.json());

// Rate Limiting
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { error: 'Too many requests, please try again after 15 minutes.' }
});
app.use('/api/', apiLimiter);

// Sample Tickets
let tickets = [
  {
    id: 1,
    accountName: 'Acme Corp',
    issue: 'Critical API failure in payment gateway endpoint',
    category: 'Technical',
    priority: 'High',
    assignedAgent: 'Agent Alex',
    status: 'Open',
    createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    deadlineTimestamp: Date.now() + 2 * 60 * 60 * 1000,
    slaDurationHours: 2,
    rating: 0
  }
];

// Routes
app.get('/api/tickets', (req, res) => {
  res.json(tickets);
});

app.post('/api/tickets', (req, res) => {
  const { accountName, issue, category, priority, slaDurationHours, assignedAgent } = req.body;

  const newTicket = {
    id: Date.now(),
    accountName: accountName || 'General Account',
    issue: issue || 'No description provided',
    category: category || 'General',
    priority: priority || 'Medium',
    assignedAgent: assignedAgent || 'Agent Alex',
    status: 'Open',
    createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    deadlineTimestamp: Date.now() + (slaDurationHours || 8) * 60 * 60 * 1000,
    slaDurationHours: slaDurationHours || 8,
    rating: 0
  };

  tickets.unshift(newTicket);
  res.status(201).json(newTicket);
});

// Start Server
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`🔒 Secure Backend Server running on http://localhost:${PORT}`);
});