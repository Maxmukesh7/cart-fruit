/**
 * FruitCart — Main JavaScript
 * Handles: navbar scroll, mobile menu, cart badge, micro-animations
 */

// ─── Confirm JS is loaded ─────────────────────────────────────────
console.log('%c🍊 Fruit Cart loaded', 'color: #f97316; font-weight: bold; font-size: 14px;');

// ─── DOM Ready ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // ── 1. Navbar: add shadow on scroll ───────────────────────────
  const navbar = document.getElementById('main-navbar');

  if (navbar) {
    const handleNavScroll = () => {
      if (window.scrollY > 10) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    };
    window.addEventListener('scroll', handleNavScroll, { passive: true });
    handleNavScroll(); // Run once on load
  }

  // ── 2. Mobile Menu Toggle ──────────────────────────────────────
  const hamburgerBtn = document.getElementById('hamburger-btn');
  const mobileMenu   = document.getElementById('mobile-menu');

  if (hamburgerBtn && mobileMenu) {
    hamburgerBtn.addEventListener('click', () => {
      const isOpen = hamburgerBtn.classList.toggle('is-open');
      mobileMenu.classList.toggle('is-open', isOpen);

      // Update ARIA attributes for accessibility
      hamburgerBtn.setAttribute('aria-expanded', String(isOpen));
      mobileMenu.setAttribute('aria-hidden', String(!isOpen));

      // Prevent body scroll when menu is open
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    // Close mobile menu when a link is clicked
    mobileMenu.querySelectorAll('.mobile-menu__link').forEach(link => {
      link.addEventListener('click', () => {
        hamburgerBtn.classList.remove('is-open');
        mobileMenu.classList.remove('is-open');
        hamburgerBtn.setAttribute('aria-expanded', 'false');
        mobileMenu.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
      });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (
        mobileMenu.classList.contains('is-open') &&
        !mobileMenu.contains(e.target) &&
        !hamburgerBtn.contains(e.target)
      ) {
        hamburgerBtn.classList.remove('is-open');
        mobileMenu.classList.remove('is-open');
        hamburgerBtn.setAttribute('aria-expanded', 'false');
        mobileMenu.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
      }
    });
  }

  // ── 3. Cart Badge ──────────────────────────────────────────────
  // The badge count is now rendered server-side via the cart context
  // processor. No localStorage needed. The badge hides itself via
  // the .cart-badge--hidden CSS class when cart_count === 0.

  // ── 4. Scroll-reveal animation ─────────────────────────────────
  // Elements fade up when they enter the viewport.
  const revealElements = document.querySelectorAll(
    '.feature-card, .step, .hero__badge, .hero__stats'
  );

  if ('IntersectionObserver' in window && revealElements.length > 0) {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry, index) => {
          if (entry.isIntersecting) {
            // Stagger the animation
            setTimeout(() => {
              entry.target.classList.add('is-visible');
            }, index * 80);
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    // Add initial hidden state via inline style
    revealElements.forEach(el => {
      el.style.opacity  = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      revealObserver.observe(el);
    });

    // When visible, restore
    document.addEventListener('animationframe', () => {
      document.querySelectorAll('.is-visible').forEach(el => {
        el.style.opacity  = '1';
        el.style.transform = 'translateY(0)';
      });
    });

    // MutationObserver fallback to apply visible styles
    const styleObserver = new MutationObserver((mutations) => {
      mutations.forEach(mutation => {
        mutation.target.style.opacity  = '1';
        mutation.target.style.transform = 'translateY(0)';
      });
    });
    revealElements.forEach(el => {
      styleObserver.observe(el, { attributes: true, attributeFilter: ['class'] });
    });
  }

  // ── 5. Smooth scroll for anchor links ─────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href').slice(1);
      const target   = document.getElementById(targetId);
      if (target) {
        e.preventDefault();
        const navbarH = navbar ? navbar.offsetHeight : 0;
        const top     = target.getBoundingClientRect().top + window.scrollY - navbarH - 16;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  // ── 6. Auto-dismiss flash messages ────────────────────────────
  const messages = document.querySelectorAll('.message');
  messages.forEach((msg, i) => {
    setTimeout(() => {
      msg.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      msg.style.opacity    = '0';
      msg.style.transform  = 'translateX(20px)';
      setTimeout(() => msg.remove(), 500);
    }, 4000 + i * 500); // Stagger dismissal
  });

  // ── 7. Checkout Loading State ──────────────────────────────────
  const checkoutForm = document.getElementById('checkout-form');
  if (checkoutForm) {
    checkoutForm.addEventListener('submit', function (e) {
      const btn = document.getElementById('place-order-btn');
      if (btn && !btn.disabled) {
        // Form will still submit, but button is disabled
        btn.disabled = true;
        btn.style.opacity = '0.7';
        btn.style.cursor = 'not-allowed';
        btn.innerHTML = '<span class="spinner" aria-hidden="true">↻</span> Processing...';
      }
    });
  }

  // ── 8. Cart Client-Side Validation ───────────────────────────
  const qtyInputs = document.querySelectorAll('.qty-input');
  qtyInputs.forEach(input => {
    input.addEventListener('change', (e) => {
      let val = parseInt(e.target.value, 10);
      const min = parseInt(e.target.min || 1, 10);
      const max = parseInt(e.target.max || 99, 10);
      
      if (isNaN(val) || val < min) {
        val = min;
      } else if (val > max) {
        val = max;
      }
      e.target.value = val;
    });
  });


  // ── 9. Hero photo — 3D mouse-tracking tilt ────────────────────
  // Reads mouse position relative to the card centre and maps it to
  // rotateX / rotateY, then moves the shine overlay's radial-gradient
  // origin so the specular highlight always faces the light source
  // (the cursor).  Uses lerp + rAF for smooth 60-fps updates.

  const scene = document.getElementById('hero-3d-scene');
  const card  = document.getElementById('hero-3d-card');
  const shine = document.getElementById('hero-3d-shine');

  if (scene && card && shine) {
    // Config
    const MAX_ROT_X  = 18;   // degrees vertical tilt
    const MAX_ROT_Y  = 22;   // degrees horizontal tilt
    const LERP_SPEED = 0.10; // 0–1 — lower = smoother/laggier

    let targetRX = 0, targetRY = 0;
    let currentRX = 0, currentRY = 0;
    let rafId = null;
    let isHovering = false;

    function lerp(a, b, t) { return a + (b - a) * t; }

    function tick() {
      currentRX = lerp(currentRX, targetRX, LERP_SPEED);
      currentRY = lerp(currentRY, targetRY, LERP_SPEED);

      card.style.transform =
        `rotateX(${currentRX.toFixed(2)}deg) rotateY(${currentRY.toFixed(2)}deg) scale(1.03)`;

      // Shift shine: map rotation to a percentage position
      // rotateY positive → light moves right; rotateX negative → light moves up
      const shineX = 50 + (currentRY / MAX_ROT_Y) * 35;   // 15%–85%
      const shineY = 50 - (currentRX / MAX_ROT_X) * 35;   // 15%–85%
      shine.style.background =
        `radial-gradient(circle at ${shineX.toFixed(1)}% ${shineY.toFixed(1)}%,` +
        `rgba(255,255,255,0.32) 0%, rgba(255,255,255,0.10) 35%, transparent 65%)`;

      if (isHovering || Math.abs(currentRX) > 0.05 || Math.abs(currentRY) > 0.05) {
        rafId = requestAnimationFrame(tick);
      } else {
        rafId = null; // done easing, stop the loop
      }
    }

    scene.addEventListener('mousemove', function (e) {
      const rect = card.getBoundingClientRect();
      const cx   = rect.left + rect.width  / 2;
      const cy   = rect.top  + rect.height / 2;
      const dx   = (e.clientX - cx) / (rect.width  / 2); // –1 to +1
      const dy   = (e.clientY - cy) / (rect.height / 2);

      targetRY =  dx * MAX_ROT_Y;   // right → positive rotateY
      targetRX = -dy * MAX_ROT_X;   // down  → negative rotateX (tip top toward viewer)

      if (!rafId) { rafId = requestAnimationFrame(tick); }
    });

    scene.addEventListener('mouseenter', function () {
      isHovering = true;
      card.classList.add('is-tracking');
      card.style.transition = 'none'; // let rAF own the transform
    });

    scene.addEventListener('mouseleave', function () {
      isHovering = false;
      targetRX = 0;
      targetRY = 0;
      // Ease back via CSS transition, then hand back to the CSS animation
      card.style.transition = 'transform 0.6s ease';
      card.style.transform  = 'rotateX(0deg) rotateY(0deg) scale(1)';
      // Reset shine
      shine.style.background = '';
      // After transition, restore idle CSS animation
      setTimeout(function () {
        card.classList.remove('is-tracking');
        card.style.transition = '';
        card.style.transform  = '';
      }, 650);
      if (!rafId) { rafId = requestAnimationFrame(tick); } // finish lerp
    });
  }

  // ── 10. Card image qty overlay — − / + buttons ────────────────
  // Uses event delegation so it works for every fruit card without
  // needing to query all buttons individually.
  // Each button carries data-form="{form-id}" and (for +) data-max="{stock}".
  // On click we read/write the hidden <input name="quantity"> inside
  // the linked form, then refresh the visible display span.

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.card-qty-btn');
    if (!btn) return;

    // Stop the click bubbling to the <a> image link
    e.preventDefault();
    e.stopPropagation();

    const formId  = btn.dataset.form;
    const form    = document.getElementById(formId);
    if (!form) return;

    const qtyInput  = form.querySelector('input[name="quantity"]');
    if (!qtyInput) return;

    // Derive the slug from the form id: "add-form-{slug}"
    const slug      = formId.replace('add-form-', '');
    const display   = document.getElementById('qty-display-' + slug);
    const isInc     = btn.classList.contains('card-qty-btn--inc');
    const max       = parseInt(btn.dataset.max || '99', 10);

    let current = parseInt(qtyInput.value, 10) || 1;
    if (isInc) {
      current = Math.min(current + 1, max);
    } else {
      current = Math.max(current - 1, 1);
    }

    qtyInput.value = current;
    if (display) display.textContent = current;
  });

  // ── 11. AJAX Add to Cart Submission ────────────────────────────
  document.addEventListener('submit', function (e) {
    const form = e.target.closest('form[action*="/cart/add/"]');
    if (!form) return;

    // Prevent default form page reload
    e.preventDefault();

    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return;

    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;

    const formData = new FormData(form);

    fetch(form.action, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Server error');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Update navbar cart badge immediately
        const cartBadge = document.getElementById('cart-badge');
        if (cartBadge) {
          cartBadge.textContent = data.cart_count;
          if (data.cart_count > 0) {
            cartBadge.classList.remove('cart-badge--hidden');
          } else {
            cartBadge.classList.add('cart-badge--hidden');
          }
        }

        // Temporarily change clicked button text to "Added ✓"
        submitBtn.innerHTML = 'Added ✓';

        // Show a small success toast
        showToast(data.message, data.msg_type || 'success');

        // Restore button state
        setTimeout(() => {
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
        }, 1500);
      } else {
        showToast(data.message || 'Could not add to cart.', 'error');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
      }
    })
    .catch(error => {
      console.error('Error adding to cart:', error);
      showToast('Could not add item to cart. Falling back...', 'error');
      
      // Traditional fallback: submit the form without AJAX if fetch fails
      form.submit();
    });
  });

  // ── 12. Toast Notification Helpers ─────────────────────────────
  function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-notification--${type}`;
    toast.innerHTML = `
      <div class="toast-notification__body">${message}</div>
      <button type="button" class="toast-notification__close" aria-label="Close">✕</button>
    `;

    container.appendChild(toast);

    toast.querySelector('.toast-notification__close').addEventListener('click', () => {
      dismissToast(toast);
    });

    setTimeout(() => {
      dismissToast(toast);
    }, 3500);
  }

  function dismissToast(toast) {
    toast.classList.add('toast-notification--fade-out');
    toast.addEventListener('transitionend', () => {
      toast.remove();
      const container = document.querySelector('.toast-container');
      if (container && container.children.length === 0) {
        container.remove();
      }
    });
  }

  // Expose globally
  window.showToast = showToast;

  console.log('✅ FruitCart JS initialised — all systems go!');
});
