/**
 * cart.js - Cart page behavior for Flask Clothing E-commerce App
 * Depends on main.js (fetchAPI, showToast, updateCartCount, formatPrice)
 */

/**
 * addToCart: Adds a product item to the user's shopping cart
 * Can be invoked from shop listing page, quick view modal, or detail page
 *
 * @param {string|number} productId - Product ID
 * @param {string|null} size - Selected size
 * @param {string|null} color - Selected color
 * @param {number} quantity - Item quantity
 * @returns {Promise<Object|null>} API response
 */
async function addToCart(productId, size = null, color = null, quantity = 1) {
  if (!productId) {
    showToast('Product ID is missing', 'error');
    return null;
  }

  try {
    const payload = {
      product_id: productId,
      size: size || null,
      color: color || null,
      quantity: parseInt(quantity, 10) || 1
    };

    const response = await fetchAPI('/api/cart', {
      method: 'POST',
      body: payload
    });

    if (response && response.success !== false) {
      showToast('Item added to cart!', 'success');
      await updateCartCount();
      return response;
    } else {
      showToast(response.error || 'Failed to add item to cart', 'error');
      return null;
    }
  } catch (error) {
    showToast(error.message || 'Error adding item to cart', 'error');
    return null;
  }
}

/**
 * updateQuantity: Updates quantity of an existing cart item
 * If quantity is set to 0, item is automatically removed from cart
 *
 * @param {string|number} itemId - Cart item ID
 * @param {number} quantity - New item quantity
 */
async function updateQuantity(itemId, quantity) {
  const newQty = parseInt(quantity, 10);

  // If quantity <= 0, remove the item
  if (isNaN(newQty) || newQty <= 0) {
    return await removeItem(itemId);
  }

  try {
    const response = await fetchAPI(`/api/cart/${itemId}`, {
      method: 'PUT',
      body: { quantity: newQty }
    });

    if (response && response.success !== false) {
      // Locate cart row DOM element
      const itemRow = document.querySelector(`[data-cart-item-id="${itemId}"]`) ||
                      document.querySelector(`[data-item-id="${itemId}"]`) ||
                      document.querySelector(`#cart-item-${itemId}`);

      if (itemRow) {
        const itemPriceEl = itemRow.querySelector('.item-price') || itemRow.querySelector('[data-price]');
        const subtotalEl = itemRow.querySelector('.item-subtotal') || itemRow.querySelector('[data-subtotal]');
        const qtyInput = itemRow.querySelector('.qty-input') || itemRow.querySelector('input[name="quantity"]');

        if (qtyInput && parseInt(qtyInput.value, 10) !== newQty) {
          qtyInput.value = newQty;
        }

        // Calculate and update row subtotal display
        let unitPrice = 0;
        if (response.data && response.data.item && typeof response.data.item.price === 'number') {
          unitPrice = response.data.item.price;
        } else if (itemPriceEl) {
          unitPrice = parseFloat(itemPriceEl.dataset.price || itemPriceEl.textContent.replace(/[^0-9.]/g, '')) || 0;
        }

        if (subtotalEl && unitPrice > 0) {
          const rowSubtotal = unitPrice * newQty;
          subtotalEl.dataset.subtotal = rowSubtotal;
          subtotalEl.textContent = formatPrice(rowSubtotal);
        }
      }

      // If backend returns updated cart data, re-render or update overall totals
      if (response.data && response.data.items) {
        renderCart(response.data);
      } else {
        updateCartTotals();
      }

      await updateCartCount();
      showToast('Cart updated', 'success');
    } else {
      showToast(response.error || 'Failed to update item quantity', 'error');
    }
  } catch (error) {
    showToast(error.message || 'Error updating cart quantity', 'error');
  }
}

/**
 * removeItem: Removes an item from the cart
 *
 * @param {string|number} itemId - Cart item ID
 */
async function removeItem(itemId) {
  try {
    const response = await fetchAPI(`/api/cart/${itemId}`, {
      method: 'DELETE'
    });

    if (response && response.success !== false) {
      const itemRow = document.querySelector(`[data-cart-item-id="${itemId}"]`) ||
                      document.querySelector(`[data-item-id="${itemId}"]`) ||
                      document.querySelector(`#cart-item-${itemId}`);

      if (itemRow) {
        // Animate row removal
        itemRow.style.transition = 'all 0.3s ease';
        itemRow.style.opacity = '0';
        itemRow.style.transform = 'translateX(-20px)';

        setTimeout(() => {
          itemRow.remove();

          // Check if cart is empty after row deletion
          const remainingRows = document.querySelectorAll('[data-cart-item-id], [data-item-id], .cart-item-row');
          if (remainingRows.length === 0) {
            showEmptyCartState();
          } else {
            updateCartTotals();
          }
        }, 300);
      } else if (response.data) {
        renderCart(response.data);
      }

      await updateCartCount();
      showToast('Item removed from cart', 'success');
    } else {
      showToast(response.error || 'Failed to remove item', 'error');
    }
  } catch (error) {
    showToast(error.message || 'Error removing item from cart', 'error');
  }
}

/**
 * showEmptyCartState: Displays the empty state UI on the cart page
 */
function showEmptyCartState() {
  const cartContainer = document.querySelector('#cart-content') || document.querySelector('.cart-container') || document.querySelector('#cartContainer');
  const emptyContainer = document.querySelector('#cart-empty') || document.querySelector('.cart-empty-state') || document.querySelector('#cartEmpty');

  if (cartContainer) {
    cartContainer.style.display = 'none';
  }

  if (emptyContainer) {
    emptyContainer.style.display = 'block';
    emptyContainer.classList.remove('d-none', 'hidden');
  } else if (cartContainer && cartContainer.parentNode) {
    const emptyWrapper = document.createElement('div');
    emptyWrapper.id = 'cart-empty';
    emptyWrapper.className = 'text-center py-5';
    emptyWrapper.innerHTML = `
      <div class="empty-cart-icon mb-3" style="font-size: 3rem;">🛒</div>
      <h3>Your Shopping Cart is Empty</h3>
      <p class="text-muted">Looks like you haven't added any clothing items yet.</p>
      <a href="/products" class="btn btn-primary mt-3">Start Shopping</a>
    `;
    cartContainer.parentNode.appendChild(emptyWrapper);
  }
}

/**
 * renderCart: Renders or updates cart DOM elements from API data response
 *
 * @param {Object} cartData - Data object returned by GET /api/cart
 */
function renderCart(cartData) {
  if (!cartData) return;

  const items = cartData.items || (Array.isArray(cartData) ? cartData : []);
  const cartItemsList = document.querySelector('#cart-items-list') || document.querySelector('.cart-items') || document.querySelector('#cartItems');

  if (items.length === 0) {
    showEmptyCartState();
    return;
  }

  const cartContainer = document.querySelector('#cart-content') || document.querySelector('.cart-container') || document.querySelector('#cartContainer');
  const emptyContainer = document.querySelector('#cart-empty') || document.querySelector('.cart-empty-state') || document.querySelector('#cartEmpty');

  if (cartContainer) cartContainer.style.display = 'block';
  if (emptyContainer) emptyContainer.style.display = 'none';

  if (cartItemsList) {
    cartItemsList.innerHTML = items.map(item => {
      const itemId = item.id || item.item_id;
      const product = item.product || item;
      const unitPrice = item.price || product.price || 0;
      const qty = item.quantity || 1;
      const subtotal = item.subtotal || (unitPrice * qty);

      return `
        <div class="cart-item-row d-flex align-items-center justify-content-between p-3 border-bottom" data-item-id="${itemId}" data-cart-item-id="${itemId}">
          <div class="cart-item-info d-flex align-items-center gap-3">
            <img src="${product.image_url || '/static/images/placeholder.jpg'}" alt="${escapeHTML(product.name || 'Product')}" class="cart-item-img" style="width: 70px; height: 70px; object-fit: cover; border-radius: 6px;">
            <div>
              <h5 class="cart-item-title mb-1">${escapeHTML(product.name || 'Product')}</h5>
              <div class="cart-item-meta text-muted small">
                ${item.size ? `<span class="me-2">Size: <strong>${escapeHTML(item.size)}</strong></span>` : ''}
                ${item.color ? `<span>Color: <strong>${escapeHTML(item.color)}</strong></span>` : ''}
              </div>
              <div class="item-price text-muted small mt-1" data-price="${unitPrice}">${formatPrice(unitPrice)} each</div>
            </div>
          </div>

          <div class="cart-item-actions d-flex align-items-center gap-3">
            <div class="quantity-control d-flex align-items-center border rounded">
              <button type="button" class="btn btn-sm btn-light qty-btn" data-action="decrease-qty" data-item-id="${itemId}">-</button>
              <input type="number" class="form-control form-control-sm text-center qty-input" style="width: 50px; border: none;" value="${qty}" min="1" data-item-id="${itemId}">
              <button type="button" class="btn btn-sm btn-light qty-btn" data-action="increase-qty" data-item-id="${itemId}">+</button>
            </div>

            <div class="item-subtotal fw-bold ms-3" data-subtotal="${subtotal}" style="min-width: 80px; text-align: right;">
              ${formatPrice(subtotal)}
            </div>

            <button type="button" class="btn btn-sm btn-outline-danger remove-item-btn" data-action="remove-item" data-item-id="${itemId}" title="Remove item">
              &times;
            </button>
          </div>
        </div>
      `;
    }).join('');
  }

  // Recalculate cart totals
  updateCartTotals(cartData);
}

/**
 * updateCartTotals: Recalculates subtotal, shipping, and total values from cart items
 *
 * @param {Object} [cartData] - Optional pre-computed cart object from API
 */
function updateCartTotals(cartData) {
  let subtotal = 0;

  if (cartData && typeof cartData.subtotal === 'number') {
    subtotal = cartData.subtotal;
  } else {
    // Sum subtotals from active DOM item rows
    const itemRows = document.querySelectorAll('[data-cart-item-id], [data-item-id], .cart-item-row');
    itemRows.forEach(row => {
      const priceEl = row.querySelector('.item-price') || row.querySelector('[data-price]');
      const qtyInput = row.querySelector('.qty-input') || row.querySelector('input[type="number"]');

      if (priceEl && qtyInput) {
        const price = parseFloat(priceEl.dataset.price || priceEl.textContent.replace(/[^0-9.]/g, '')) || 0;
        const qty = parseInt(qtyInput.value, 10) || 0;
        subtotal += price * qty;
      } else {
        const subtotalEl = row.querySelector('.item-subtotal') || row.querySelector('[data-subtotal]');
        if (subtotalEl) {
          subtotal += parseFloat(subtotalEl.dataset.subtotal || subtotalEl.textContent.replace(/[^0-9.]/g, '')) || 0;
        }
      }
    });
  }

  // Shipping calculation
  let shipping = 0;
  if (cartData && typeof cartData.shipping === 'number') {
    shipping = cartData.shipping;
  } else if (subtotal > 0) {
    const shippingEl = document.querySelector('.cart-shipping') || document.querySelector('#cart-shipping') || document.querySelector('[data-shipping]');
    if (shippingEl && shippingEl.dataset.shippingRate) {
      shipping = parseFloat(shippingEl.dataset.shippingRate) || 0;
    } else {
      shipping = subtotal > 100 ? 0 : 10; // Free shipping over $100
    }
  }

  const total = subtotal + shipping;

  // Update DOM elements for summary
  document.querySelectorAll('.cart-subtotal, #cart-subtotal, [data-cart-subtotal]').forEach(el => {
    el.textContent = formatPrice(subtotal);
  });

  document.querySelectorAll('.cart-shipping, #cart-shipping, [data-cart-shipping]').forEach(el => {
    el.textContent = shipping === 0 && subtotal > 0 ? 'FREE' : formatPrice(shipping);
  });

  document.querySelectorAll('.cart-total, #cart-total, [data-cart-total]').forEach(el => {
    el.textContent = formatPrice(total);
  });
}

/**
 * loadCartPage: Initializer function when viewing the cart page
 */
async function loadCartPage() {
  const cartContainer = document.querySelector('#cart-content') || document.querySelector('.cart-container') || document.querySelector('#cartContainer');
  if (!cartContainer) return; // Not on cart page

  try {
    const response = await fetchAPI('/api/cart');
    if (response && response.data) {
      renderCart(response.data);
    }
  } catch (error) {
    console.warn('Failed to load initial cart page state:', error.message);
  }
}

// DOMContentLoaded Initialization & Event Delegation for Cart Behavior
document.addEventListener('DOMContentLoaded', () => {
  // Load initial cart content if on cart page
  loadCartPage();

  // Event Delegation for Add-to-Cart, Quantity Buttons, and Remove Buttons
  document.addEventListener('click', async (e) => {
    // 1. Add to Cart Button (data-action="add-to-cart" or .add-to-cart-btn)
    const addBtn = e.target.closest('[data-action="add-to-cart"], .add-to-cart-btn');
    if (addBtn) {
      e.preventDefault();
      const productId = addBtn.dataset.productId || addBtn.getAttribute('data-product-id');
      const size = addBtn.dataset.size || addBtn.getAttribute('data-size') || null;
      const color = addBtn.dataset.color || addBtn.getAttribute('data-color') || null;
      const qtyInput = document.querySelector(`input[data-product-id="${productId}"]`) || document.querySelector('#quantity');
      const quantity = qtyInput ? parseInt(qtyInput.value, 10) : (parseInt(addBtn.dataset.quantity, 10) || 1);

      const originalText = addBtn.innerHTML;
      addBtn.disabled = true;
      addBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Adding...';

      try {
        await addToCart(productId, size, color, quantity);
      } finally {
        addBtn.disabled = false;
        addBtn.innerHTML = originalText;
      }
      return;
    }

    // 2. Quantity Increase Button
    const incBtn = e.target.closest('[data-action="increase-qty"]');
    if (incBtn) {
      e.preventDefault();
      const itemId = incBtn.dataset.itemId || incBtn.getAttribute('data-item-id');
      const row = incBtn.closest('[data-item-id], [data-cart-item-id], .cart-item-row') || incBtn.parentElement;
      const input = row ? row.querySelector('.qty-input, input[type="number"]') : null;
      if (input) {
        const newQty = (parseInt(input.value, 10) || 0) + 1;
        input.value = newQty;
        if (itemId) {
          updateQuantity(itemId, newQty);
        }
      }
      return;
    }

    // 3. Quantity Decrease Button
    const decBtn = e.target.closest('[data-action="decrease-qty"]');
    if (decBtn) {
      e.preventDefault();
      const itemId = decBtn.dataset.itemId || decBtn.getAttribute('data-item-id');
      const row = decBtn.closest('[data-item-id], [data-cart-item-id], .cart-item-row') || decBtn.parentElement;
      const input = row ? row.querySelector('.qty-input, input[type="number"]') : null;
      if (input) {
        const currentQty = parseInt(input.value, 10) || 1;
        const newQty = currentQty - 1;
        if (newQty <= 0) {
          if (itemId) removeItem(itemId);
        } else {
          input.value = newQty;
          if (itemId) updateQuantity(itemId, newQty);
        }
      }
      return;
    }

    // 4. Remove Item Button
    const removeBtn = e.target.closest('[data-action="remove-item"], .remove-item-btn');
    if (removeBtn) {
      e.preventDefault();
      const itemId = removeBtn.dataset.itemId || removeBtn.getAttribute('data-item-id');
      if (itemId) {
        removeItem(itemId);
      }
      return;
    }

    // 5. Checkout Button
    const checkoutBtn = e.target.closest('#checkout-btn, [data-action="checkout"], .btn-checkout');
    if (checkoutBtn) {
      e.preventDefault();
      window.location.href = '/checkout';
      return;
    }
  });

  // Direct input change event listener for quantity input boxes
  document.addEventListener('change', (e) => {
    if (e.target.matches('.qty-input') || e.target.matches('input[data-action="update-qty"]')) {
      const input = e.target;
      const itemId = input.dataset.itemId || input.getAttribute('data-item-id');
      const newQty = parseInt(input.value, 10);

      if (itemId) {
        if (isNaN(newQty) || newQty <= 0) {
          removeItem(itemId);
        } else {
          updateQuantity(itemId, newQty);
        }
      }
    }
  });
});

// Expose cart functions globally
window.addToCart = addToCart;
window.updateQuantity = updateQuantity;
window.removeItem = removeItem;
window.renderCart = renderCart;
window.updateCartTotals = updateCartTotals;
