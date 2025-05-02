document.addEventListener('DOMContentLoaded', () => {
  // CART UI ELEMENTS
  const cartBtn     = document.getElementById('cart-btn');
  const cartModal   = document.getElementById('cart-modal');
  const closeCart   = document.getElementById('close-cart');
  const cartCount   = document.getElementById('cart-count');
  const cartList    = document.getElementById('cart-list');
  const checkoutBtn = document.getElementById('checkout-btn');

  // Helpers to load/save cart in localStorage
  function getCart() {
    return JSON.parse(localStorage.getItem('cart') || '[]');
  }
  function saveCart(c) {
    localStorage.setItem('cart', JSON.stringify(c));
  }

  // Update the badge count
  function updateCartCount() {
    cartCount.textContent = getCart().length;
  }

  // Render cart items in the modal
  function renderCart() {
    const c = getCart();
    if (c.length === 0) {
      cartList.innerHTML = '<p>Your cart is empty.</p>';
      checkoutBtn.disabled = true;
      return;
    }
    checkoutBtn.disabled = false;
    cartList.innerHTML = c.map((item, idx) => `
      <div class="cart-item" data-index="${idx}">
        <img src="${item.img}" alt="${item.address}">
        <div class="cart-item-details">
          <h4>${item.address}</h4>
          <p>${item.start} → ${item.end}</p>
          <p class="price">${item.price}</p>
        </div>
        <button class="remove-btn" data-index="${idx}">&times;</button>
      </div>
    `).join('');

    // Wire up remove buttons
    document.querySelectorAll('.remove-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        const i = +e.target.dataset.index;
        const cart = getCart();
        cart.splice(i, 1);
        saveCart(cart);
        updateCartCount();
        renderCart();
      });
    });
  }

  // Open/close cart modal
  cartBtn.addEventListener('click', e => {
    e.preventDefault();
    renderCart();
    cartModal.style.display = 'flex';
  });
  closeCart.addEventListener('click', () => cartModal.style.display = 'none');
  window.addEventListener('click', e => {
    if (e.target === cartModal) cartModal.style.display = 'none';
  });

  // “Book” handler: require login, then create booking & redirect
  checkoutBtn.addEventListener('click', async () => {
    // 1) Must be logged in
    if (!window.appConfig?.userEmail) {
      alert('You must sign in to book. Redirecting to login page...');
      window.location.href = '/login';
      return;
    }

    // 2) Create booking for first cart item
    const cart = getCart();
    if (cart.length === 0) return;

    const item = cart[0];
    try {
      const resp = await fetch(window.appConfig.bookingApi, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          property_id: item.property_id,
          user_email:   window.appConfig.userEmail,
          start_date:   item.start,
          end_date:     item.end
        })
      });
      if (!resp.ok) throw new Error(`Booking failed (${resp.status})`);
      const data = await resp.json();
      const bookingId = data.booking.booking_id;
      window.location.href = `/payments/${bookingId}`;
    } catch (err) {
      alert('Error creating booking: ' + err.message);
    }
  });

  // SEARCH & LISTINGS
  const form    = document.getElementById('search-form');
  const locIn   = document.getElementById('location-search');
  const ciIn    = document.getElementById('check-in');
  const coIn    = document.getElementById('check-out');
  const results = document.getElementById('results');

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const q = locIn.value.trim();
    if (!q) return;

    try {
      const resp = await fetch(`/api/properties?location=${encodeURIComponent(q)}`);
      if (!resp.ok) throw new Error(`Error ${resp.status}`);
      const list = await resp.json();
      if (!list.length) {
        results.innerHTML = `<p>No rentals for “${q}.”</p>`;
        return;
      }

      results.innerHTML = list.map(item => {
        const addr  = item.location?.address || {};
        const img   = item.primary_photo?.href || 'https://via.placeholder.com/400x300';
        const sd    = ciIn.value || 'N/A';
        const ed    = coIn.value || 'N/A';
        const price = item.list_price ? `$${item.list_price}` : 'N/A';
        return `
          <div class="listing-card">
            <img src="${img}" alt="Property">
            <h3>${addr.line || 'Unknown'}, ${addr.city || ''}</h3>
            <p>Price: ${price}</p>
            <button
              class="cart-btn"
              data-id="${item.property_id}"
              data-address="${addr.line || addr.city}"
              data-start="${sd}"
              data-end="${ed}"
              data-img="${img}"
              data-price="${price}"
            >Add to Cart</button>
          </div>
        `;
      }).join('');

      // Wire “Add to Cart” buttons
      document.querySelectorAll('.listing-card .cart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          // Must be logged in to add to cart
          if (!window.appConfig?.userEmail) {
            alert('You must sign in to add to cart. Redirecting to login...');
            return window.location.href = '/login';
          }
          const cart = getCart();
          cart.push({
            property_id: btn.dataset.id,
            address:     btn.dataset.address,
            start:       btn.dataset.start,
            end:         btn.dataset.end,
            img:         btn.dataset.img,
            price:       btn.dataset.price
          });
          saveCart(cart);
          updateCartCount();
        });
      });

    } catch (err) {
      results.innerHTML = `<p>${err.message}</p>`;
    }
  });

  // Initialize badge count
  updateCartCount();
});
