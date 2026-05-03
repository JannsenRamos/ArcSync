const mongoose = require('mongoose');

const reviewSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  rating: { type: Number, required: true, min: 1, max: 5 },
  comment: { type: String, maxlength: 500 },
  createdAt: { type: Date, default: Date.now }
});

const productSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true, maxlength: 200 },
  slug: { type: String, unique: true, lowercase: true },
  description: { type: String, required: true, maxlength: 2000 },
  price: { type: Number, required: true, min: 0 },
  compareAtPrice: { type: Number, min: 0 },
  category: {
    type: String,
    required: true,
    enum: ['electronics', 'clothing', 'books', 'home', 'sports', 'toys']
  },
  tags: [{ type: String, trim: true }],
  images: [{
    url: { type: String, required: true },
    alt: { type: String },
    isPrimary: { type: Boolean, default: false }
  }],
  inventory: {
    quantity: { type: Number, required: true, min: 0, default: 0 },
    sku: { type: String, unique: true },
    trackInventory: { type: Boolean, default: true }
  },
  reviews: [reviewSchema],
  averageRating: { type: Number, default: 0 },
  isActive: { type: Boolean, default: true },
  vendor: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }
}, {
  timestamps: true,
  toJSON: { virtuals: true }
});

productSchema.index({ name: 'text', description: 'text' });
productSchema.index({ category: 1, price: 1 });
productSchema.index({ slug: 1 });

productSchema.virtual('isOnSale').get(function() {
  return this.compareAtPrice && this.compareAtPrice > this.price;
});

productSchema.methods.updateAverageRating = function() {
  if (this.reviews.length === 0) {
    this.averageRating = 0;
  } else {
    const sum = this.reviews.reduce((acc, r) => acc + r.rating, 0);
    this.averageRating = Math.round((sum / this.reviews.length) * 10) / 10;
  }
};

module.exports = mongoose.model('Product', productSchema);
