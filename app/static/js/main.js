/**
 * main.js - Shared utilities loaded on every page for Flask Clothing E-commerce App
 */

// CSRF token extracted from meta tag in base.html head
const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';

/**
 * fetchAPI: Wrapper for all fetch API calls across the application.
 * Automatically adds Content-Type and CSRF headers, handles HTTP errors, and parses JSON.
 *
 * @param {string} url - The API endpoint URL
 * @param {Object} options - Standard fetch options (method, headers, body, etc.)
 * @returns {Promise<Object>} Resolves to parsed response data
 */
async function fetchAPI(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase();

  const headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': CSRF_TOKEN,
    'X-CSRF-TOKEN': CSRF_TOKEN,
    ...(options.headers || {})
  };

  const config = {
    ...options,
    method,
    headers
  };

  // Stringify JSON body for non-GET requests if body is an object/array
  if (method !== 'GET' && config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
  }

  // GET requests must not contain a body
  if (method === 'GET') {
    delete config.body;
  }

  try {
    const response = await fetch(url, config);

    // Handle standard HTTP error status codes
    if (response.status === 401) {
      showToast('Session expired. Please log in.', 'error');
      setTimeout(() => {
        const currentPath = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/login?next=${currentPath}`;
      }, 1200);
      throw new Error('Unauthorized (401)');
    }

    if (response.status === 403) {
      showToast('Access denied. You do not have permission for this action.', 'error');
      throw new Error('Forbidden (403)');
    }

    if (response.status >= 500) {
      showToast('Server error occurred. Please try again later.', 'error');
      throw new Error(`Server Error (${response.status})`);
    }

    // Parse JSON body
    let data;
    try {
      data = await response.json();
    } catch (parseErr) {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      throw new Error('Invalid JSON response from server');
    }

    // Check application-level success property
    if (!response.ok || (data && data.success === false)) {
      const errorMessage = (data && data.error) || `Request failed with status ${response.status}`;
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    console.error(`API Error [${method} ${url}]:`, error);
    throw error;
  }
}

/**
 * updateCartCount: Syncs navbar cart count badge with current server cart state.
 * Handles errors gracefully without breaking page execution.
 */
async function updateCartCount() {
  try {
    const response = await fetchAPI('/api/cart');
    let totalCount = 0;

    if (response && response.data) {
      const items = response.data.items || (Array.isArray(response.data) ? response.data : null);
      if (items && Array.isArray(items)) {
        totalCount = items.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0);
      } else if (typeof response.data.total_items === 'number') {
        totalCount = response.data.total_items;
      } else if (typeof response.data.count === 'number') {
        totalCount = response.data.count;
      }
    }

    const cartBadges = document.querySelectorAll('.cart-badge');
    cartBadges.forEach(badge => {
      badge.textContent = totalCount;
      if (totalCount > 0) {
        badge.classList.remove('d-none', 'hidden');
      } else {
        badge.textContent = '0';
      }
    });
  } catch (error) {
    // Log error gracefully; do not throw or alert the user
    console.warn('Could not update cart badge count:', error.message);
  }
}

/**
 * showToast: Renders a floating notification toast inside #toastContainer.
 *
 * @param {string} message - Notification text
 * @param {string} type - Toast type ('success', 'error', 'info', 'warning')
 * @param {number} duration - Timeout before auto-dismissal (ms)
 */
function showToast(message, type = 'success', duration = 3000) {
  let container = document.getElementById('toastContainer');

  // Create toast container dynamically if missing from layout
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1090';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  const typeClass = type === 'error' ? 'toast-error' : (type === 'warning' ? 'toast-warning' : 'toast-success');

  toast.className = `toast-item ${typeClass} show`;
  toast.role = 'alert';
  toast.ariaLive = 'assertive';
  toast.ariaAtomic = 'true';

  const iconMarkup = type === 'error'
    ? '<span class="toast-icon">✕</span>'
    : (type === 'warning' ? '<span class="toast-icon">⚠️</span>' : '<span class="toast-icon">✓</span>');

  toast.innerHTML = `
    <div class="toast-content d-flex align-items-center justify-content-between gap-3">
      <div class="d-flex align-items-center gap-2">
        ${iconMarkup}
        <span class="toast-message">${escapeHTML(message)}</span>
      </div>
      <button type="button" class="btn-close-toast" aria-label="Close" style="background:none;border:none;font-size:1.2rem;line-height:1;cursor:pointer;">&times;</button>
    </div>
  `;

  // Manual dismiss handler
  const closeBtn = toast.querySelector('.btn-close-toast');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => removeToast(toast));
  }

  container.appendChild(toast);

  // Auto remove timer
  const timer = setTimeout(() => {
    removeToast(toast);
  }, duration);

  function removeToast(el) {
    clearTimeout(timer);
    el.classList.add('fade-out');
    el.style.opacity = '0';
    el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    el.style.transform = 'translateY(10px)';
    setTimeout(() => {
      if (el.parentNode) {
        el.parentNode.removeChild(el);
      }
    }, 300);
  }
}

/**
 * escapeHTML: Helper function to escape special characters for HTML injection
 *
 * @param {string} str - Raw string
 * @returns {string} Sanitized string
 */
function escapeHTML(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.innerText = str;
  return div.innerHTML;
}

/**
 * formatPrice: Formats raw number as currency string
 *
 * @param {number|string} amount
 * @returns {string} Formatted price string (e.g. "$19.99")
 */
function formatPrice(amount) {
  const num = Number(amount);
  if (isNaN(num)) return '$0.00';
  return '$' + num.toFixed(2);
}

/**
 * debounce: Delays function execution until after specified wait time
 *
 * @param {Function} func - Function to debounce
 * @param {number} wait - Delay in milliseconds
 * @returns {Function}
 */
function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func.apply(this, args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * validateForm: Performs basic client-side form validation
 *
 * @param {HTMLFormElement} form - Form DOM element to validate
 * @returns {boolean} True if form is valid, false otherwise
 */
function validateForm(form) {
  if (!form || !(form instanceof HTMLFormElement)) return false;

  let isValid = true;
  const inputs = form.querySelectorAll('input, select, textarea');

  // Clear previous validation error messages
  form.querySelectorAll('.error-feedback, .invalid-feedback').forEach(el => el.remove());
  form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

  inputs.forEach(input => {
    let fieldValid = true;
    let errorMessage = '';

    if (input.type === 'hidden' || input.disabled) return;

    // Required field validation
    if (input.hasAttribute('required') && !input.value.trim()) {
      fieldValid = false;
      errorMessage = 'This field is required.';
    }

    // Email format validation
    if (fieldValid && input.type === 'email' && input.value.trim()) {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(input.value.trim())) {
        fieldValid = false;
        errorMessage = 'Please enter a valid email address.';
      }
    }

    // Password / Text length validation
    if (fieldValid && input.hasAttribute('minlength')) {
      const minLength = parseInt(input.getAttribute('minlength'), 10);
      if (input.value.length < minLength) {
        fieldValid = false;
        errorMessage = `Must be at least ${minLength} characters.`;
      }
    }

    // Password confirmation matching validation
    if (fieldValid && input.dataset.match) {
      const targetInput = form.querySelector(input.dataset.match);
      if (targetInput && input.value !== targetInput.value) {
        fieldValid = false;
        errorMessage = 'Passwords do not match.';
      }
    }

    if (!fieldValid) {
      isValid = false;
      input.classList.add('is-invalid');
      const errorDiv = document.createElement('div');
      errorDiv.className = 'invalid-feedback error-feedback text-danger small mt-1';
      errorDiv.textContent = errorMessage;
      
      if (input.nextSibling) {
        input.parentNode.insertBefore(errorDiv, input.nextSibling);
      } else {
        input.parentNode.appendChild(errorDiv);
      }
    }
  });

  return isValid;
}

/**
 * initGlobalSearch: Configures real-time debounced global product search
 */
function initGlobalSearch() {
  const searchInput = document.querySelector('[data-search-input]') || document.querySelector('#globalSearch') || document.querySelector('.search-input');
  const searchForm = document.querySelector('[data-search-form]') || document.querySelector('#searchForm');

  if (searchInput) {
    const handleSearch = debounce(async (query) => {
      query = query.trim();
      const resultsContainer = document.querySelector('#searchResults') || document.querySelector('.search-results-dropdown');

      if (!resultsContainer) return;

      if (query.length < 2) {
        resultsContainer.classList.remove('show');
        return;
      }

      try {
        const res = await fetchAPI(`/api/products?q=${encodeURIComponent(query)}&per_page=5`);
        const products = res.data?.products || (Array.isArray(res.data) ? res.data : []);

        if (products.length > 0) {
          resultsContainer.innerHTML = products.map(p => `
            <a href="/products/${p.id}" class="search-result-item d-flex align-items-center p-2 text-decoration-none border-bottom">
              <img src="${p.image_url || '/static/images/placeholder.jpg'}" alt="${escapeHTML(p.name)}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" class="me-2">
              <div>
                <div class="fw-bold text-dark small">${escapeHTML(p.name)}</div>
                <div class="text-muted small">${formatPrice(p.price)}</div>
              </div>
            </a>
          `).join('');
          resultsContainer.classList.add('show');
        } else {
          resultsContainer.innerHTML = `<div class="p-3 text-muted small text-center">No products found</div>`;
          resultsContainer.classList.add('show');
        }
      } catch (error) {
        console.warn('Global search lookup error:', error);
      }
    }, 300);

    searchInput.addEventListener('input', (e) => handleSearch(e.target.value));

    // Hide search results dropdown when clicking outside
    document.addEventListener('click', (e) => {
      const resultsContainer = document.querySelector('#searchResults') || document.querySelector('.search-results-dropdown');
      if (resultsContainer && !searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
        resultsContainer.classList.remove('show');
      }
    });
  }

  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      const input = searchForm.querySelector('input[name="q"]') || searchInput;
      if (input && !input.value.trim()) {
        e.preventDefault();
      }
    });
  }
}

/**
 * initFlashMessages: Sets up auto-dismissal for standard Flask flash alerts
 */
function initFlashMessages() {
  const flashAlerts = document.querySelectorAll('.alert-dismissible, .flash-message');
  flashAlerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 5000);

    const closeBtn = alert.querySelector('.btn-close, .close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => alert.remove());
    }
  });
}

// Global initialization on DOM load
document.addEventListener('DOMContentLoaded', () => {
  // Sync initial navbar cart badge count
  updateCartCount();

  // Initialize global navbar search handler
  initGlobalSearch();

  // Auto dismiss flash notification banners
  initFlashMessages();
});

// Expose utilities on window object for global page scripts
window.CSRF_TOKEN = CSRF_TOKEN;
window.fetchAPI = fetchAPI;
window.updateCartCount = updateCartCount;
window.showToast = showToast;
window.formatPrice = formatPrice;
window.debounce = debounce;
window.validateForm = validateForm;
window.escapeHTML = escapeHTML;
