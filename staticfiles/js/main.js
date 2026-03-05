// Portfolio Main JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // ===== MOBILE MENU TOGGLE (FIXED) =====
  const mobileMenuBtn = document.querySelector(".mobile-menu-btn");
  const mobileMenu = document.querySelector(".mobile-menu");
  const mobileMenuBackdrop = document.querySelector(".mobile-menu-backdrop");

  // Create backdrop if it doesn't exist
  if (!mobileMenuBackdrop) {
    const backdrop = document.createElement("div");
    backdrop.className = "mobile-menu-backdrop";
    document.body.appendChild(backdrop);
    backdrop.addEventListener("click", closeMobileMenu);
  }

  function toggleMobileMenu() {
    mobileMenu.classList.toggle("active");
    const icon = mobileMenuBtn.querySelector("i");

    if (mobileMenu.classList.contains("active")) {
      icon.classList.remove("fa-bars");
      icon.classList.add("fa-times");
      document.body.style.overflow = "hidden"; // Prevent scrolling
      document.querySelector(".mobile-menu-backdrop").style.display = "block";
    } else {
      icon.classList.remove("fa-times");
      icon.classList.add("fa-bars");
      document.body.style.overflow = ""; // Restore scrolling
      document.querySelector(".mobile-menu-backdrop").style.display = "none";
    }
  }

  function closeMobileMenu() {
    if (mobileMenu.classList.contains("active")) {
      mobileMenu.classList.remove("active");
      const icon = mobileMenuBtn.querySelector("i");
      icon.classList.remove("fa-times");
      icon.classList.add("fa-bars");
      document.body.style.overflow = ""; // Restore scrolling
      document.querySelector(".mobile-menu-backdrop").style.display = "none";
    }
  }

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener("click", function (e) {
      e.stopPropagation(); // Prevent event from bubbling up
      toggleMobileMenu();
    });

    // Close menu when clicking outside (via backdrop)
    document.addEventListener("click", function (event) {
      if (
        !mobileMenu.contains(event.target) &&
        !mobileMenuBtn.contains(event.target) &&
        mobileMenu.classList.contains("active")
      ) {
        closeMobileMenu();
      }
    });

    // Close menu when clicking a link
    document.querySelectorAll(".mobile-nav-link, .nav-link").forEach((link) => {
      link.addEventListener("click", function () {
        closeMobileMenu();
      });
    });

    // Close menu on escape key
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && mobileMenu.classList.contains("active")) {
        closeMobileMenu();
      }
    });

    // Close menu on window resize (if resizing to desktop)
    window.addEventListener("resize", function () {
      if (window.innerWidth > 768 && mobileMenu.classList.contains("active")) {
        closeMobileMenu();
      }
    });
  }

  // ===== DARK MODE TOGGLE =====
  const darkModeToggle = document.getElementById("darkModeToggle");
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  // Check for saved theme or preferred scheme
  const currentTheme = localStorage.getItem("theme");
  if (currentTheme === "dark" || (!currentTheme && prefersDarkScheme.matches)) {
    document.body.classList.add("dark-mode");
    if (darkModeToggle) {
      darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
  }

  if (darkModeToggle) {
    darkModeToggle.addEventListener("click", function () {
      document.body.classList.toggle("dark-mode");

      if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
        this.innerHTML = '<i class="fas fa-sun"></i>';
      } else {
        localStorage.setItem("theme", "light");
        this.innerHTML = '<i class="fas fa-moon"></i>';
      }
    });
  }

  // ===== SMOOTH SCROLLING =====
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (href === "#" || href === "#!") return;

      e.preventDefault();
      const targetElement = document.querySelector(href);
      if (targetElement) {
        // Close mobile menu if open
        if (mobileMenu && mobileMenuBtn) {
          closeMobileMenu();
        }

        const topOffset = 80;
        const targetTop =
          targetElement.getBoundingClientRect().top +
          window.scrollY -
          topOffset;

        window.scrollTo({
          top: targetTop,
          behavior: "smooth",
        });
      }
    });
  });

  // ===== SCROLL REVEAL ANIMATION =====
  const revealTargets = document.querySelectorAll(
    ".section, .project-card, .timeline-item, .skill-item, .profile-card",
  );
  if ("IntersectionObserver" in window && revealTargets.length > 0) {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add(
              "animate__animated",
              "animate__fadeInUp",
            );
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.12,
        rootMargin: "0px 0px -40px 0px",
      },
    );

    revealTargets.forEach((target) => revealObserver.observe(target));
  }

  // ... Rest of your existing code (form validation, notifications, etc.) ...
  // KEEP ALL YOUR EXISTING CODE BELOW THIS LINE
  // ===== FORM VALIDATION =====
  // ... (keep your existing form validation code) ...

  // ===== NOTIFICATION SYSTEM =====
  // ... (keep your existing notification code) ...

  // ===== SKILL PROGRESS BARS ANIMATION =====
  // ... (keep your existing skill bars code) ...

  // ===== LAZY LOAD IMAGES =====
  // ... (keep your existing lazy load code) ...

  // ===== BACK TO TOP BUTTON =====
  // ... (keep your existing back to top code) ...

  // ===== NAVBAR SCROLL EFFECT =====
  // ... (keep your existing navbar scroll code) ...

  // ===== PROJECT FILTERING =====
  // ... (keep your existing project filtering code) ...

  // ===== COPY EMAIL TO CLIPBOARD =====
  // ... (keep your existing copy email code) ...

  // ===== INITIALIZE TOOLTIPS =====
  // ... (keep your existing tooltips code) ...

  // ===== THEME COLOR PICKER (DEMO) =====
  // ... (keep your existing theme picker code) ...

  // ===== PRINT FUNCTIONALITY =====
  // ... (keep your existing print code) ...
});

// ===== UTILITY FUNCTIONS =====
// ... (keep your existing utility functions) ...
