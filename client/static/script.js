document.addEventListener('DOMContentLoaded', () => {
  // ── Cart UI ──────────────────────────────────────────────────
  const cartBtn     = document.getElementById('cart-btn');
  const cartModal   = document.getElementById('cart-modal');
  const closeCart   = document.getElementById('close-cart');
  const cartCountEl = document.getElementById('cart-count');
  const cartList    = document.getElementById('cart-list');
  const checkoutBtn = document.getElementById('checkout-btn');

  function getCart() {
    return JSON.parse(localStorage.getItem('cart') || '[]');
  }
  function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
  }
  function updateCartCount() {
    if (cartCountEl) cartCountEl.textContent = getCart().length;
  }
  function renderCart() {
    const items = getCart();
    if (!cartList || !checkoutBtn) return;
    if (items.length === 0) {
      cartList.innerHTML = '<p>Your cart is empty.</p>';
      checkoutBtn.disabled = true;
      return;
    }
    checkoutBtn.disabled = false;
    cartList.innerHTML = items.map((item, idx) => `
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
    document.querySelectorAll('.remove-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        const i = Number(e.target.dataset.index);
        const cartArr = getCart();
        cartArr.splice(i, 1);
        saveCart(cartArr);
        updateCartCount();
        renderCart();
      });
    });
  }

  if (cartBtn && cartModal) {
    cartBtn.addEventListener('click', e => {
      e.preventDefault();
      renderCart();
      cartModal.style.display = 'flex';
    });
    closeCart.addEventListener('click', () => cartModal.style.display = 'none');
    window.addEventListener('click', e => {
      if (e.target === cartModal) cartModal.style.display = 'none';
    });
  }

  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', async () => {
      if (!window.appConfig?.userEmail) {
        alert('You must sign in to book. Redirecting to login...');
        window.location.href = '/login';
        return;
      }
      const cartArr = getCart();
      if (!cartArr.length) return;
      const item = cartArr[0];
      try {
        const resp = await fetch(window.appConfig.bookingApi, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            property_id: item.property_id,
            start_date:  item.start,
            end_date:    item.end
          })
        });
        if (!resp.ok) throw new Error(`Booking failed (${resp.status})`);
        const { booking } = await resp.json();
        localStorage.removeItem('cart');
        updateCartCount();
        window.location.href = `/payments/${booking.booking_id}`;
      } catch (err) {
        alert('Error creating booking: ' + err.message);
      }
    });
  }

  // ── Search + Merge Host Listings ────────────────────────────
  const form    = document.getElementById('search-form');
  const locIn   = document.getElementById('location-search');
  const ciIn    = document.getElementById('check-in');
  const coIn    = document.getElementById('check-out');
  const results = document.getElementById('results');

  if (form && results) {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const q = locIn.value.trim();
      if (!q) return;

      // 1) fetch external rentals, treating 404 as empty
      let extList = [];
      try {
        const resp = await fetch(`/api/properties?location=${encodeURIComponent(q)}`);
        if (resp.ok) {
          extList = await resp.json();
        } else if (resp.status === 404) {
          extList = [];
        } else {
          throw new Error(`Error ${resp.status}`);
        }
      } catch (err) {
        console.error('External properties error:', err);
        extList = [];
      }

      // 2) fetch host listings
      const hostResp = await fetch('/api/listings');
      const hostList = hostResp.ok ? await hostResp.json() : [];

      // 3) filter & map host listings into same shape
      const term = q.toLowerCase();
      const hostMatches = hostList
        .filter(l => 
          (l.address || '').toLowerCase().includes(term) ||
          (l.title   || '').toLowerCase().includes(term)
        )
        .map(l => ({
          property_id:   l.id,
          location:      { address: { line: l.title, city: l.address } },
          primary_photo: { href: l.image_url },
          list_price:    l.price
        }));

      // 4) combine both arrays
      const combined = [...extList, ...hostMatches];

      // 5) render results
      if (!combined.length) {
        results.innerHTML = `<p>No rentals for “${q}.”</p>`;
      } else {
        results.innerHTML = combined.map(item => {
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
              <button
                class="review-btn"
                data-id="${item.property_id}"
                style="margin-top:0.5rem;"
              >Reviews</button>
            </div>
          `;
        }).join('');
      }

      // 6) wire “Add to Cart”
      document.querySelectorAll('.listing-card .cart-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          if (!window.appConfig?.userEmail) {
            alert('You must sign in to add to cart. Redirecting to login...');
            return window.location.href = '/login';
          }
          const cartArr = getCart();
          cartArr.push({
            property_id: btn.dataset.id,
            address:     btn.dataset.address,
            start:       btn.dataset.start,
            end:         btn.dataset.end,
            img:         btn.dataset.img,
            price:       btn.dataset.price
          });
          saveCart(cartArr);
          updateCartCount();
        });
      });

      // 7) wire “Reviews”
      document.querySelectorAll('.listing-card .review-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          window.location.href = `/reviews/${btn.dataset.id}`;
        });
      });
    });
  }

  // initialize badge
  updateCartCount();
});
