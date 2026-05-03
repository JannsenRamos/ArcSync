const express = require('express');
const router = express.Router();
const Order = require('../models/order');
const Product = require('../models/product');
const { authenticate, authorize } = require('../middleware/auth');

// POST /api/orders - Create new order
router.post('/', authenticate, async (req, res) => {
  try {
    const { items, shippingAddress, paymentMethod } = req.body;
    if (!items || items.length === 0) return res.status(400).json({ error: 'No order items' });

    let subtotal = 0;
    const orderItems = [];
    for (const item of items) {
      const product = await Product.findById(item.product);
      if (!product) return res.status(404).json({ error: `Product ${item.product} not found` });
      if (product.inventory.quantity < item.quantity) {
        return res.status(400).json({ error: `Insufficient stock for ${product.name}` });
      }
      orderItems.push({ product: product._id, name: product.name, quantity: item.quantity, price: product.price, image: product.images[0]?.url });
      subtotal += product.price * item.quantity;
      product.inventory.quantity -= item.quantity;
      await product.save();
    }

    const taxAmount = subtotal * 0.08;
    const shippingCost = subtotal > 50 ? 0 : 9.99;
    const totalAmount = subtotal + taxAmount + shippingCost;

    const order = new Order({ user: req.user.id, items: orderItems, shippingAddress, paymentMethod, subtotal, taxAmount, shippingCost, totalAmount });
    await order.save();
    res.status(201).json(order);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// GET /api/orders - List user orders
router.get('/', authenticate, async (req, res) => {
  try {
    const orders = await Order.find({ user: req.user.id }).sort({ createdAt: -1 });
    res.json(orders);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch orders' });
  }
});

// PUT /api/orders/:id/status - Update order status (admin)
router.put('/:id/status', authenticate, authorize('admin'), async (req, res) => {
  try {
    const order = await Order.findByIdAndUpdate(req.params.id, { status: req.body.status }, { new: true });
    if (!order) return res.status(404).json({ error: 'Order not found' });
    res.json(order);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

module.exports = router;
