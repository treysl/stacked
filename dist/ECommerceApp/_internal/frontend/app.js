// API Configuration
const API_BASE_URL = 'http://localhost:8001';

// Token management
function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
}

function getAuthHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
}

// Cart management
function getCart() {
    const cart = localStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartCount() {
    const cart = getCart();
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartCountElements = document.querySelectorAll('#cart-count');
    cartCountElements.forEach(el => {
        if (el) el.textContent = count;
    });
}

function addToCart(productId, productName, price, stock) {
    const cart = getCart();
    const existingItem = cart.find(item => item.product_id === productId);
    
    if (existingItem) {
        if (existingItem.quantity < stock) {
            existingItem.quantity++;
        } else {
            alert('Cannot add more items. Stock limit reached.');
            return;
        }
    } else {
        cart.push({
            product_id: productId,
            product_name: productName,
            price: price,
            quantity: 1
        });
    }
    
    saveCart(cart);
    updateCartCount();
    alert('Product added to cart!');
}

function removeFromCart(productId) {
    const cart = getCart();
    const filteredCart = cart.filter(item => item.product_id !== productId);
    saveCart(filteredCart);
    updateCartCount();
    if (typeof loadCart === 'function') {
        loadCart();
    }
}

function updateCartQuantity(productId, quantity) {
    const cart = getCart();
    const item = cart.find(item => item.product_id === productId);
    if (item) {
        if (quantity <= 0) {
            removeFromCart(productId);
        } else {
            item.quantity = quantity;
            saveCart(cart);
            updateCartCount();
            if (typeof loadCart === 'function') {
                loadCart();
            }
        }
    }
}

// Authentication
async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            setToken(data.access_token);
            alert('Login successful!');
            window.location.href = 'index.html';
        } else {
            document.getElementById('login-error').textContent = data.detail || 'Login failed';
        }
    } catch (error) {
        document.getElementById('login-error').textContent = 'Error connecting to server';
    }
}

async function register(username, email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            document.querySelector('.tab-btn[data-tab="login"]').click();
        } else {
            document.getElementById('register-error').textContent = data.detail || 'Registration failed';
        }
    } catch (error) {
        document.getElementById('register-error').textContent = 'Error connecting to server';
    }
}

function logout() {
    removeToken();
    saveCart([]);
    window.location.href = 'index.html';
}

function checkAuthStatus() {
    const token = getToken();
    const loginLink = document.getElementById('login-link');
    const userInfo = document.getElementById('user-info');
    const logoutBtn = document.getElementById('logout-btn');
    
    if (token) {
        if (loginLink) loginLink.style.display = 'none';
        if (userInfo) userInfo.style.display = 'inline';
        if (logoutBtn) {
            logoutBtn.style.display = 'inline-block';
            logoutBtn.addEventListener('click', logout);
        }
    } else {
        if (loginLink) loginLink.style.display = 'inline';
        if (userInfo) userInfo.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

// Product loading
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/products`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const products = await response.json();
        
        const container = document.getElementById('products-container');
        if (!container) return;
        
        if (products.length === 0) {
            container.innerHTML = '<p>No products available.</p>';
            return;
        }
        
        container.innerHTML = products.map(product => `
            <div class="product-card">
                <h3>${product.product_name}</h3>
                <p class="price">$${product.price.toFixed(2)}</p>
                <p class="stock">Stock: ${product.stock_quantity}</p>
                <p style="font-size: 0.9rem; color: #666; margin: 0.5rem 0;">
                    ${product.description || ''}
                </p>
                <button 
                    onclick="addToCart(${product.id}, '${product.product_name.replace(/'/g, "\\'")}', ${product.price}, ${product.stock_quantity})"
                    ${product.stock_quantity === 0 ? 'disabled' : ''}
                >
                    ${product.stock_quantity === 0 ? 'Out of Stock' : 'Add to Cart'}
                </button>
            </div>
        `).join('');
    } catch (error) {
        const container = document.getElementById('products-container');
        if (container) {
            let errorMsg = 'Error loading products. ';
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                errorMsg += 'Cannot connect to backend server. ';
                errorMsg += 'Make sure the backend is running on http://localhost:8001';
                if (window.location.protocol === 'file:') {
                    errorMsg += '<br><br><strong>Note:</strong> You are opening the HTML file directly. ';
                    errorMsg += 'Please use a local web server instead (see README.md for instructions).';
                }
            } else {
                errorMsg += error.message;
            }
            container.innerHTML = `<p style="color: red;">${errorMsg}</p>`;
        }
        console.error('Error loading products:', error);
    }
}

// Cart loading
function loadCart() {
    const cart = getCart();
    const container = document.getElementById('cart-container');
    const summary = document.getElementById('cart-summary');
    
    if (!container) return;
    
    if (cart.length === 0) {
        container.innerHTML = '<p>Your cart is empty.</p>';
        if (summary) summary.style.display = 'none';
        return;
    }
    
    let total = 0;
    container.innerHTML = cart.map(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        return `
            <div class="cart-item">
                <div class="cart-item-info">
                    <h4>${item.product_name}</h4>
                    <p>$${item.price.toFixed(2)} each</p>
                </div>
                <div class="cart-item-controls">
                    <button onclick="updateCartQuantity(${item.product_id}, ${item.quantity - 1})">-</button>
                    <span style="min-width: 30px; text-align: center;">${item.quantity}</span>
                    <button onclick="updateCartQuantity(${item.product_id}, ${item.quantity + 1})">+</button>
                    <button onclick="removeFromCart(${item.product_id})">Remove</button>
                </div>
                <div style="font-weight: bold; margin-left: 1rem;">
                    $${itemTotal.toFixed(2)}
                </div>
            </div>
        `;
    }).join('');
    
    if (summary) {
        summary.style.display = 'block';
        document.getElementById('cart-total').textContent = total.toFixed(2);
    }
}

// Checkout
async function checkout() {
    const token = getToken();
    if (!token) {
        alert('Please login to checkout');
        window.location.href = 'login.html';
        return;
    }
    
    const cart = getCart();
    if (cart.length === 0) {
        alert('Your cart is empty');
        return;
    }
    
    // Calculate total
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    // Prepare order items
    const items = cart.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.price
    }));
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/orders`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                items: items,
                total_amount: total
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`Order placed successfully! Order ID: ${data.order_id}`);
            saveCart([]);
            updateCartCount();
            window.location.href = 'orders.html';
        } else {
            alert(data.detail || 'Failed to place order');
        }
    } catch (error) {
        alert('Error connecting to server');
    }
}

// Order loading
async function loadOrders() {
    const token = getToken();
    const container = document.getElementById('orders-container');
    
    if (!container) return;
    
    if (!token) {
        container.innerHTML = '<p>Please login to view your orders.</p>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/orders`, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            container.innerHTML = '<p>Please login to view your orders.</p>';
            removeToken();
            checkAuthStatus();
            return;
        }
        
        const orders = await response.json();
        
        if (orders.length === 0) {
            container.innerHTML = '<p>You have no orders yet.</p>';
            return;
        }
        
        container.innerHTML = orders.map(order => {
            const orderDate = new Date(order.order_date);
            return `
                <div class="order-card">
                    <div class="order-header">
                        <div>
                            <strong>Order ID:</strong> ${order.order_id}<br>
                            <strong>Date:</strong> ${orderDate.toLocaleDateString()}<br>
                            <strong>Status:</strong> ${order.order_status}
                        </div>
                        <div style="text-align: right;">
                            <strong>Total: $${order.total_amount.toFixed(2)}</strong>
                        </div>
                    </div>
                    <div class="order-items">
                        <h4>Items:</h4>
                        ${order.items.map(item => `
                            <div class="order-item">
                                ${item.product_name} - Qty: ${item.quantity} @ $${item.unit_price.toFixed(2)} = $${(item.quantity * item.unit_price).toFixed(2)}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        container.innerHTML = '<p>Error loading orders. Make sure the backend server is running.</p>';
    }
}

