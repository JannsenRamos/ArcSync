# E-Commerce API

A RESTful API for an e-commerce platform built with Node.js, Express, and MongoDB.

## Tech Stack
- **Runtime**: Node.js 18+
- **Framework**: Express.js 4.x
- **Database**: MongoDB with Mongoose ODM
- **Auth**: JWT (jsonwebtoken) + bcrypt
- **Payments**: Stripe SDK
- **Validation**: Joi

## API Endpoints

### Auth
- `POST /api/auth/register` — Register new user
- `POST /api/auth/login` — Login
- `GET /api/auth/me` — Get profile
- `PUT /api/auth/me` — Update profile

### Products
- `GET /api/products` — List with filtering, search, pagination
- `GET /api/products/:id` — Get product details
- `POST /api/products` — Create (vendor/admin)
- `PUT /api/products/:id` — Update (vendor/admin)
- `POST /api/products/:id/reviews` — Add review

### Orders
- `POST /api/orders` — Create order
- `GET /api/orders` — List user orders
- `PUT /api/orders/:id/status` — Update status (admin)

## Data Models
- **User** — email, password (bcrypt), roles, addresses, wishlist
- **Product** — name, price, category, inventory, reviews, images
- **Order** — items, shipping, payment, status tracking
