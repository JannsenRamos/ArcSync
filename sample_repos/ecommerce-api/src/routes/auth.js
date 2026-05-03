const express = require('express');
const router = express.Router();
const User = require('../models/user');
const { authenticate } = require('../middleware/auth');

// POST /api/auth/register
router.post('/register', async (req, res) => {
  try {
    const { email, password, firstName, lastName } = req.body;
    const existingUser = await User.findOne({ email });
    if (existingUser) return res.status(400).json({ error: 'Email already registered' });

    const user = new User({ email, password, firstName, lastName });
    await user.save();
    const token = user.generateAuthToken();
    res.status(201).json({ user, token });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email }).select('+password');
    if (!user || !(await user.comparePassword(password))) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }
    user.lastLogin = new Date();
    await user.save();
    const token = user.generateAuthToken();
    res.json({ user, token });
  } catch (error) {
    res.status(500).json({ error: 'Login failed' });
  }
});

// GET /api/auth/me - Get current user profile
router.get('/me', authenticate, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).populate('wishlist', 'name price images');
    res.json(user);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
});

// PUT /api/auth/me - Update profile
router.put('/me', authenticate, async (req, res) => {
  try {
    const updates = ['firstName', 'lastName', 'phone', 'addresses'];
    const user = await User.findById(req.user.id);
    updates.forEach(field => { if (req.body[field] !== undefined) user[field] = req.body[field]; });
    await user.save();
    res.json(user);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

module.exports = router;
