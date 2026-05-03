const express = require('express');
const router = express.Router();
const Product = require('../models/product');
const { authenticate, authorize } = require('../middleware/auth');

// GET /api/products - List all products with filtering & pagination
router.get('/', async (req, res) => {
  try {
    const { category, minPrice, maxPrice, search, sort, page = 1, limit = 20 } = req.query;
    const filter = { isActive: true };

    if (category) filter.category = category;
    if (minPrice || maxPrice) {
      filter.price = {};
      if (minPrice) filter.price.$gte = Number(minPrice);
      if (maxPrice) filter.price.$lte = Number(maxPrice);
    }
    if (search) filter.$text = { $search: search };

    const sortOptions = {};
    if (sort === 'price_asc') sortOptions.price = 1;
    else if (sort === 'price_desc') sortOptions.price = -1;
    else if (sort === 'rating') sortOptions.averageRating = -1;
    else sortOptions.createdAt = -1;

    const products = await Product.find(filter)
      .sort(sortOptions)
      .skip((page - 1) * limit)
      .limit(Number(limit))
      .select('-reviews');

    const total = await Product.countDocuments(filter);

    res.json({
      products,
      pagination: { page: Number(page), limit: Number(limit), total, pages: Math.ceil(total / limit) }
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch products' });
  }
});

// GET /api/products/:id - Get single product
router.get('/:id', async (req, res) => {
  try {
    const product = await Product.findById(req.params.id).populate('reviews.user', 'firstName lastName');
    if (!product) return res.status(404).json({ error: 'Product not found' });
    res.json(product);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch product' });
  }
});

// POST /api/products - Create product (vendor/admin only)
router.post('/', authenticate, authorize('vendor', 'admin'), async (req, res) => {
  try {
    const product = new Product({ ...req.body, vendor: req.user.id });
    await product.save();
    res.status(201).json(product);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// PUT /api/products/:id - Update product
router.put('/:id', authenticate, authorize('vendor', 'admin'), async (req, res) => {
  try {
    const product = await Product.findByIdAndUpdate(req.params.id, req.body, { new: true, runValidators: true });
    if (!product) return res.status(404).json({ error: 'Product not found' });
    res.json(product);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// POST /api/products/:id/reviews - Add review
router.post('/:id/reviews', authenticate, async (req, res) => {
  try {
    const product = await Product.findById(req.params.id);
    if (!product) return res.status(404).json({ error: 'Product not found' });

    const existingReview = product.reviews.find(r => r.user.toString() === req.user.id);
    if (existingReview) return res.status(400).json({ error: 'You already reviewed this product' });

    product.reviews.push({ user: req.user.id, ...req.body });
    product.updateAverageRating();
    await product.save();
    res.status(201).json(product);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

module.exports = router;
