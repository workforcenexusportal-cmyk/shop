/**
 * product.js - Product detail page behavior for Flask Clothing E-commerce App
 * Depends on main.js (fetchAPI, showToast, updateCartCount)
 */

// Product Page Component State
let selectedSize = null;
let selectedColor = null;
let currentQuantity = 1;
let productStock = 99;
let currentProductId = null;

/**
 * selectSize: Selects product size variant and updates active option UI state
 *
 * @param {string} size - Selected size name (e.g., 'S', 'M', 'L', 'XL')
 * @param {HTMLElement} [element] - Optional clicked DOM element
 */
function selectSize(size, element) {
  selectedSize = size;

  // Clear size validation error state
  const sizeContainer = document.querySelector('#size-selector') || document.querySelector('.size-options');
  if (sizeContainer) {
    sizeContainer.classList.remove('is-invalid', 'border-danger');
    const errMsg = sizeContainer.parentNode.querySelector('.size-error');
    if (errMsg) errMsg.remove();
  }

  // Update button active styling
  const sizeButtons = document.querySelectorAll('[data-size], .size-btn, .size-option');
  sizeButtons.forEach(btn => {
    const btnSize = btn.dataset.size || btn.getAttribute('data-size') || btn.textContent.trim();
    if (btnSize === size || btn === element) {
      btn.classList.add('active', 'selected', 'btn-primary');
      btn.classList.remove('btn-outline-secondary', 'btn-outline-dark');
      btn.setAttribute('aria-checked', 'true');
    } else {
      btn.classList.remove('active', 'selected', 'btn-primary');
      btn.classList.add('btn-outline-secondary');
      btn.setAttribute('aria-checked', 'false');
    }
  });

  // Update selected size text label
  const selectedSizeLabel = document.querySelector('#selected-size-label') || document.querySelector('.selected-size');
  if (selectedSizeLabel) {
    selectedSizeLabel.textContent = size;
  }
}

/**
 * selectColor: Selects product color variant and updates active option UI state
 *
 * @param {string} color - Selected color name (e.g., 'Red', 'Blue', 'Black')
 * @param {HTMLElement} [element] - Optional clicked DOM element
 */
function selectColor(color, element) {
  selectedColor = color;

  // Clear color validation error state
  const colorContainer = document.querySelector('#color-selector') || document.querySelector('.color-options');
  if (colorContainer) {
    colorContainer.classList.remove('is-invalid', 'border-danger');
    const errMsg = colorContainer.parentNode.querySelector('.color-error');
    if (errMsg) errMsg.remove();
  }

  // Update swatch active styling
  const colorSwatches = document.querySelectorAll('[data-color], .color-swatch, .color-option');
  colorSwatches.forEach(swatch => {
    const swatchColor = swatch.dataset.color || swatch.getAttribute('data-color');
    if (swatchColor === color || swatch === element) {
      swatch.classList.add('active', 'selected', 'ring-2');
      swatch.setAttribute('aria-checked', 'true');
    } else {
      swatch.classList.remove('active', 'selected', 'ring-2');
      swatch.setAttribute('aria-checked', 'false');
    }
  });

  // Update selected color text label
  const selectedColorLabel = document.querySelector('#selected-color-label') || document.querySelector('.selected-color');
  if (selectedColorLabel) {
    selectedColorLabel.textContent = color;
  }
}

/**
 * changeQuantity: Increments or decrements quantity within [1, productStock] limits
 *
 * @param {number} delta - Amount to adjust quantity by (-1 or +1)
 */
function changeQuantity(delta) {
  const qtyInput = document.querySelector('#quantity') || document.querySelector('.product-quantity-input') || document.querySelector('input[name="quantity"]');

  if (qtyInput && qtyInput.max) {
    const maxVal = parseInt(qtyInput.max, 10);
    if (!isNaN(maxVal)) productStock = maxVal;
  }

  currentQuantity = Math.max(1, Math.min(productStock, currentQuantity + delta));

  if (qtyInput) {
    qtyInput.value = currentQuantity;
  }

  // Update button disabled state
  const decBtn = document.querySelector('[data-action="qty-decrease"]') || document.querySelector('.qty-minus');
  const incBtn = document.querySelector('[data-action="qty-increase"]') || document.querySelector('.qty-plus');

  if (decBtn) decBtn.disabled = currentQuantity <= 1;
  if (incBtn) incBtn.disabled = currentQuantity >= productStock;
}

/**
 * addToCart: Validates variant selection and sends POST /api/cart request
 */
async function addProductToCart() {
  const productContainer = document.querySelector('[data-product-id]') || document.querySelector('#product-detail-container');
  const productId = currentProductId || (productContainer ? productContainer.dataset.productId : null);

  if (!productId) {
    showToast('Product ID not found on page', 'error');
    return;
  }

  // Check size selection if size options are present
  const sizeContainer = document.querySelector('#size-selector') || document.querySelector('.size-options');
  const hasSizeOptions = sizeContainer && sizeContainer.querySelectorAll('[data-size], .size-btn').length > 0;

  if (hasSizeOptions && !selectedSize) {
    showToast('Please select a size before adding to cart', 'error');
    sizeContainer.classList.add('border-danger');
    return;
  }

  // Check color selection if color options are present
  const colorContainer = document.querySelector('#color-selector') || document.querySelector('.color-options');
  const hasColorOptions = colorContainer && colorContainer.querySelectorAll('[data-color], .color-swatch').length > 0;

  if (hasColorOptions && !selectedColor) {
    showToast('Please select a color before adding to cart', 'error');
    colorContainer.classList.add('border-danger');
    return;
  }

  const addToCartBtn = document.querySelector('#add-to-cart-btn') || document.querySelector('[data-action="add-product-to-cart"]');
  const originalText = addToCartBtn ? addToCartBtn.innerHTML : 'Add to Cart';

  if (addToCartBtn) {
    addToCartBtn.disabled = true;
    addToCartBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Adding...';
  }

  try {
    const response = await fetchAPI('/api/cart', {
      method: 'POST',
      body: {
        product_id: productId,
        size: selectedSize,
        color: selectedColor,
        quantity: currentQuantity
      }
    });

    if (response && response.success !== false) {
      showToast('Product added to your cart!', 'success');
      await updateCartCount();

      // Trigger mini-cart drawer if present
      const miniCart = document.querySelector('#miniCart') || document.querySelector('.mini-cart-drawer');
      if (miniCart && typeof miniCart.show === 'function') {
        miniCart.show();
      }
    } else {
      showToast(response.error || 'Failed to add item to cart', 'error');
    }
  } catch (error) {
    showToast(error.message || 'Error adding product to cart', 'error');
  } finally {
    if (addToCartBtn) {
      addToCartBtn.disabled = false;
      addToCartBtn.innerHTML = originalText;
    }
  }
}

/**
 * toggleWishlist: Adds or removes item from user wishlist via POST /api/wishlist
 *
 * @param {string|number} [productId] - Optional product ID
 * @param {HTMLElement} [btnElement] - Optional button DOM element
 */
async function toggleWishlist(productId, btnElement) {
  if (!productId) {
    const productContainer = document.querySelector('[data-product-id]');
    productId = currentProductId || (productContainer ? productContainer.dataset.productId : null);
  }

  if (!productId) {
    showToast('Product ID is missing', 'error');
    return;
  }

  const wishlistBtn = btnElement || document.querySelector('#wishlist-btn') || document.querySelector('[data-action="wishlist"]');

  if (wishlistBtn) {
    wishlistBtn.disabled = true;
  }

  try {
    const response = await fetchAPI('/api/wishlist', {
      method: 'POST',
      body: { product_id: productId }
    });

    if (response && response.success !== false) {
      const isWishlisted = response.data?.in_wishlist ?? response.data?.added ?? true;

      if (wishlistBtn) {
        wishlistBtn.classList.toggle('active', isWishlisted);
        wishlistBtn.classList.toggle('in-wishlist', isWishlisted);

        const icon = wishlistBtn.querySelector('i, svg');
        if (icon) {
          if (isWishlisted) {
            icon.classList.remove('far', 'bi-heart');
            icon.classList.add('fas', 'bi-heart-fill', 'text-danger');
          } else {
            icon.classList.remove('fas', 'bi-heart-fill', 'text-danger');
            icon.classList.add('far', 'bi-heart');
          }
        }
      }

      const msg = response.data?.message || (isWishlisted ? 'Added to your wishlist!' : 'Removed from your wishlist!');
      showToast(msg, 'success');
    } else {
      showToast(response.error || 'Failed to update wishlist', 'error');
    }
  } catch (error) {
    showToast(error.message || 'Error updating wishlist', 'error');
  } finally {
    if (wishlistBtn) {
      wishlistBtn.disabled = false;
    }
  }
}

/**
 * submitReview: Submits product rating and comment review via POST /api/reviews
 *
 * @param {string|number} [productId] - Product ID
 * @param {HTMLFormElement} [formElement] - Review form element
 */
async function submitReview(productId, formElement) {
  const form = formElement || document.querySelector('#review-form') || document.querySelector('form[data-review-form]');

  if (!form) return;

  if (!productId) {
    productId = currentProductId || form.dataset.productId || document.querySelector('[data-product-id]')?.dataset.productId;
  }

  const ratingInput = form.querySelector('input[name="rating"]:checked') || form.querySelector('#rating') || form.querySelector('[name="rating"]');
  const commentInput = form.querySelector('textarea[name="comment"]') || form.querySelector('#comment');

  const rating = ratingInput ? parseInt(ratingInput.value, 10) : 0;
  const comment = commentInput ? commentInput.value.trim() : '';

  if (!rating || rating < 1 || rating > 5) {
    showToast('Please select a star rating between 1 and 5.', 'error');
    return;
  }

  if (!comment) {
    showToast('Please enter your review comment.', 'error');
    return;
  }

  const submitBtn = form.querySelector('button[type="submit"]');
  const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Submit Review';

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Submitting...';
  }

  try {
    const response = await fetchAPI('/api/reviews', {
      method: 'POST',
      body: {
        product_id: productId,
        rating: rating,
        comment: comment
      }
    });

    if (response && response.success !== false) {
      showToast('Thank you! Your review has been submitted.', 'success');

      const reviewData = response.data?.review || {
        rating: rating,
        comment: comment,
        created_at: 'Just now',
        user_name: response.data?.user_name || 'You'
      };

      appendReviewToList(reviewData);
      form.reset();
    } else {
      showToast(response.error || 'Failed to submit review', 'error');
    }
  } catch (error) {
    showToast(error.message || 'Error submitting review', 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
    }
  }
}

/**
 * appendReviewToList: Dynamically prepends a new review card into the reviews container
 *
 * @param {Object} review - Review data object
 */
function appendReviewToList(review) {
  const reviewsContainer = document.querySelector('#reviews-list') || document.querySelector('.reviews-container') || document.querySelector('#reviewsList');
  if (!reviewsContainer) return;

  const noReviewsMsg = reviewsContainer.querySelector('.no-reviews');
  if (noReviewsMsg) noReviewsMsg.remove();

  const stars = '★'.repeat(review.rating || 5) + '☆'.repeat(5 - (review.rating || 5));

  const reviewCard = document.createElement('div');
  reviewCard.className = 'review-card card mb-3 p-3 border-light shadow-sm fade-in';
  reviewCard.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-2">
      <div class="fw-bold text-dark">${escapeHTML(review.user_name || review.author || 'Verified Buyer')}</div>
      <div class="text-warning small">${stars}</div>
    </div>
    <p class="review-text text-secondary mb-1 small">${escapeHTML(review.comment)}</p>
    <div class="text-muted text-end extra-small" style="font-size: 0.75rem;">${escapeHTML(review.created_at || 'Just now')}</div>
  `;

  reviewsContainer.prepend(reviewCard);
}

/**
 * initImageGallery: Sets up thumbnail switching and zoom/lightbox on main product image
 */
function initImageGallery() {
  const mainImage = document.querySelector('#main-product-image') || document.querySelector('.main-product-img') || document.querySelector('[data-main-image]');
  const thumbnails = document.querySelectorAll('.thumbnail-img, [data-thumb-img], .gallery-thumb');

  if (mainImage && thumbnails.length > 0) {
    thumbnails.forEach(thumb => {
      thumb.addEventListener('click', (e) => {
        e.preventDefault();
        const newSrc = thumb.dataset.fullSrc || thumb.dataset.src || thumb.src || thumb.getAttribute('href');

        if (newSrc && mainImage) {
          mainImage.src = newSrc;

          thumbnails.forEach(t => t.classList.remove('active', 'border-primary'));
          thumb.classList.add('active', 'border-primary');
        }
      });
    });
  }

  // Lightbox modal or toggle zoom on main image click
  if (mainImage) {
    mainImage.addEventListener('click', () => {
      const modal = document.querySelector('#imageLightboxModal') || document.querySelector('.image-lightbox');
      if (modal) {
        const modalImg = modal.querySelector('img');
        if (modalImg) modalImg.src = mainImage.src;
        if (typeof modal.show === 'function') {
          modal.show();
        } else {
          modal.classList.add('show');
          modal.style.display = 'block';
        }
      } else {
        mainImage.classList.toggle('zoomed-in');
      }
    });
  }
}

/**
 * checkWishlistStatus: Sets initial heart icon state if pre-rendered as wishlisted
 */
async function checkWishlistStatus() {
  if (!currentProductId) return;

  const wishlistBtn = document.querySelector('#wishlist-btn') || document.querySelector('[data-action="wishlist"]');
  if (!wishlistBtn) return;

  if (wishlistBtn.dataset.inWishlist === 'true' || wishlistBtn.dataset.wishlisted === 'true') {
    wishlistBtn.classList.add('active', 'in-wishlist');
    const icon = wishlistBtn.querySelector('i, svg');
    if (icon) {
      icon.classList.remove('far', 'bi-heart');
      icon.classList.add('fas', 'bi-heart-fill', 'text-danger');
    }
  }
}

// DOMContentLoaded Event Listeners for Product Detail Page
document.addEventListener('DOMContentLoaded', () => {
  // Read current product ID from container element
  const productContainer = document.querySelector('[data-product-id]') || document.querySelector('#product-detail-container');
  if (productContainer) {
    currentProductId = productContainer.dataset.productId || productContainer.getAttribute('data-product-id');
    if (productContainer.dataset.stock) {
      productStock = parseInt(productContainer.dataset.stock, 10) || 99;
    }
  }

  // Attach size selection listeners
  const sizeButtons = document.querySelectorAll('.size-btn, [data-size], .size-option');
  sizeButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const size = btn.dataset.size || btn.getAttribute('data-size') || btn.textContent.trim();
      selectSize(size, btn);
    });
  });

  // Attach color selection listeners
  const colorSwatches = document.querySelectorAll('.color-swatch, [data-color], .color-option');
  colorSwatches.forEach(swatch => {
    swatch.addEventListener('click', (e) => {
      e.preventDefault();
      const color = swatch.dataset.color || swatch.getAttribute('data-color');
      selectColor(color, swatch);
    });
  });

  // Attach quantity +/- button listeners
  const decBtn = document.querySelector('[data-action="qty-decrease"]') || document.querySelector('.qty-minus');
  const incBtn = document.querySelector('[data-action="qty-increase"]') || document.querySelector('.qty-plus');
  const qtyInput = document.querySelector('#quantity') || document.querySelector('.product-quantity-input');

  if (decBtn) {
    decBtn.addEventListener('click', (e) => {
      e.preventDefault();
      changeQuantity(-1);
    });
  }

  if (incBtn) {
    incBtn.addEventListener('click', (e) => {
      e.preventDefault();
      changeQuantity(1);
    });
  }

  if (qtyInput) {
    qtyInput.addEventListener('change', (e) => {
      const val = parseInt(e.target.value, 10);
      if (!isNaN(val) && val >= 1) {
        currentQuantity = Math.min(productStock, val);
        e.target.value = currentQuantity;
      } else {
        e.target.value = currentQuantity;
      }
    });
  }

  // Attach add-to-cart button listener
  const addToCartBtn = document.querySelector('#add-to-cart-btn') || document.querySelector('[data-action="add-product-to-cart"]');
  if (addToCartBtn) {
    addToCartBtn.addEventListener('click', (e) => {
      e.preventDefault();
      addProductToCart();
    });
  }

  // Attach wishlist button listener
  const wishlistBtn = document.querySelector('#wishlist-btn') || document.querySelector('[data-action="wishlist"]');
  if (wishlistBtn) {
    wishlistBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const pId = wishlistBtn.dataset.productId || currentProductId;
      toggleWishlist(pId, wishlistBtn);
    });
  }

  // Attach review form submission listener
  const reviewForm = document.querySelector('#review-form') || document.querySelector('form[data-review-form]');
  if (reviewForm) {
    reviewForm.addEventListener('submit', (e) => {
      e.preventDefault();
      submitReview(currentProductId, reviewForm);
    });
  }

  // Initialize gallery controls
  initImageGallery();

  // Check initial wishlist button status
  checkWishlistStatus();
});

// Expose product functions globally
window.selectSize = selectSize;
window.selectColor = selectColor;
window.changeQuantity = changeQuantity;
window.addProductToCart = addProductToCart;
window.toggleWishlist = toggleWishlist;
window.submitReview = submitReview;
