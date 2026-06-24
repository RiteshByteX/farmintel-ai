// script.js - Firebase Authentication Version
import { 
  auth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  sendPasswordResetEmail,
  onAuthStateChanged,
  signOut,
  updateProfile,
  sendEmailVerification,
  googleProvider,
  githubProvider
} from './firebase-config.js';

document.addEventListener("DOMContentLoaded", function () {
  // AOS init
  AOS.init({
    duration: 800,
    once: true,
    offset: 100,
  });

  // Navbar scroll effect
  const navbar = document.getElementById("navbar");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  });

  // Counter animation
  const counters = document.querySelectorAll(".counter");
  const speed = 50;

  const animateCounter = (counter) => {
    const target = parseInt(counter.getAttribute("data-target"));
    let count = 0;
    const increment = target / speed;

    const updateCount = () => {
      if (count < target) {
        count += increment;
        counter.innerText = Math.ceil(count);
        setTimeout(updateCount, 30);
      } else {
        counter.innerText = target;
      }
    };
    updateCount();
  };

  const observerOptions = { threshold: 0.5 };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  counters.forEach((counter) => observer.observe(counter));

  // Particles generation
  function createParticles() {
    const particlesContainer = document.getElementById("particles");
    for (let i = 0; i < 50; i++) {
      const particle = document.createElement("div");
      particle.classList.add("particle");
      particle.style.width = Math.random() * 5 + "px";
      particle.style.height = particle.style.width;
      particle.style.left = Math.random() * 100 + "%";
      particle.style.bottom = "-10px";
      particle.style.animationDelay = Math.random() * 15 + "s";
      particle.style.animationDuration = 10 + Math.random() * 10 + "s";
      particlesContainer.appendChild(particle);
    }
  }
  createParticles();

  // ============ FIREBASE AUTH STATE ============
  const authButtons = document.getElementById('authButtons');
  const userButtons = document.getElementById('userButtons');
  const userNameDisplay = document.getElementById('userNameDisplay');

  // Check auth state
  onAuthStateChanged(auth, (user) => {
    if (user) {
      // User is signed in
      authButtons.style.display = 'none';
      userButtons.style.display = 'flex';
      userNameDisplay.textContent = user.displayName || user.email || 'User';
      
      // Store user in localStorage for other pages
      localStorage.setItem('farmintel_current_user', JSON.stringify({
        id: user.uid,
        name: user.displayName || user.email?.split('@')[0] || 'User',
        email: user.email,
        photoURL: user.photoURL,
        role: 'farmer' // Default role
      }));
      
      console.log('✅ User logged in:', user);
    } else {
      // User is signed out
      authButtons.style.display = 'flex';
      userButtons.style.display = 'none';
      localStorage.removeItem('farmintel_current_user');
      console.log('👤 User signed out');
    }
  });

  // ============ TOAST NOTIFICATION ============
  function showToast(message, type = "info") {
    const existingToast = document.querySelector(".toast-notification");
    if (existingToast) existingToast.remove();

    const toast = document.createElement("div");
    toast.className = `toast-notification ${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <i class="fas ${type === "error" ? "fa-exclamation-circle" : type === "success" ? "fa-check-circle" : "fa-info-circle"}"></i>
        <span>${message}</span>
      </div>
      <button class="toast-close">&times;</button>
    `;

    document.body.appendChild(toast);

    toast.querySelector(".toast-close").addEventListener("click", () => {
      toast.remove();
    });

    setTimeout(() => {
      if (toast.parentNode) {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(-50%) translateY(20px)";
        setTimeout(() => toast.remove(), 300);
      }
    }, 4000);
  }

  // ============ MODAL HANDLING ============
  const loginModal = document.getElementById("loginModal");
  const signupModal = document.getElementById("signupModal");
  const forgotPasswordModal = document.getElementById("forgotPasswordModal");

  function openModal(modal) {
    modal.style.display = "flex";
    document.body.classList.add("modal-open");
  }

  function closeModal(modal) {
    modal.style.display = "none";
    document.body.classList.remove("modal-open");
  }

  document.getElementById("loginBtn").onclick = () => openModal(loginModal);
  document.getElementById("signupBtn").onclick = () => openModal(signupModal);
  document.getElementById("getStartedBtn").onclick = () => openModal(signupModal);
  document.getElementById("ctaGetStartedBtn").onclick = () => openModal(signupModal);

  document.querySelectorAll(".modal-close").forEach((btn) => {
    btn.onclick = () => {
      const modal = btn.closest(".modal");
      closeModal(modal);
    };
  });

  window.onclick = (e) => {
    if (e.target.classList.contains("modal")) {
      closeModal(e.target);
    }
  };

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const openModals = document.querySelectorAll('.modal[style*="display: flex"]');
      openModals.forEach((modal) => closeModal(modal));
    }
  });

  // Switch between modals
  document.getElementById("switchToSignup").onclick = (e) => {
    e.preventDefault();
    closeModal(loginModal);
    setTimeout(() => openModal(signupModal), 200);
  };

  document.getElementById("switchToLogin").onclick = (e) => {
    e.preventDefault();
    closeModal(signupModal);
    setTimeout(() => openModal(loginModal), 200);
  };

  document.getElementById("switchToLoginFromReset").onclick = (e) => {
    e.preventDefault();
    closeModal(forgotPasswordModal);
    setTimeout(() => openModal(loginModal), 200);
  };

  // Forgot Password link
  document.getElementById("forgotPasswordLink").onclick = (e) => {
    e.preventDefault();
    closeModal(loginModal);
    setTimeout(() => openModal(forgotPasswordModal), 200);
  };

  // ============ PASSWORD TOGGLE ============
  document.querySelectorAll(".toggle-password").forEach((btn) => {
    btn.addEventListener("click", function () {
      const wrapper = this.closest(".password-wrapper");
      const input = wrapper.querySelector(".input-field");
      const icon = this.querySelector("i");

      if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
      } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
      }
    });
  });

  // ============ PASSWORD STRENGTH ============
  const signupPassword = document.getElementById("signupPassword");
  const strengthLevel = document.getElementById("strengthLevel");
  const strengthText = document.getElementById("strengthText");
  const requirements = document.querySelectorAll(".requirement");
  const confirmPassword = document.getElementById("signupConfirmPassword");
  const passwordMatch = document.getElementById("passwordMatch");

  function checkPasswordStrength(password) {
    let score = 0;
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };

    requirements.forEach((req) => {
      const rule = req.dataset.rule;
      if (checks[rule]) {
        req.classList.add("met");
      } else {
        req.classList.remove("met");
      }
    });

    Object.values(checks).forEach((check) => {
      if (check) score++;
    });

    strengthLevel.className = "strength-level";
    if (password.length === 0) {
      strengthLevel.style.width = "0%";
      strengthText.innerHTML =
        '<i class="fas fa-shield-alt"></i><span>Use 8+ characters with a mix of letters, numbers & symbols</span>';
      return;
    }

    if (score <= 1) {
      strengthLevel.classList.add("weak");
      strengthText.innerHTML =
        '<i class="fas fa-exclamation-triangle" style="color:#EF4444;"></i><span style="color:#EF4444;">Weak password - add more variety</span>';
    } else if (score === 2) {
      strengthLevel.classList.add("medium");
      strengthText.innerHTML =
        '<i class="fas fa-exclamation-circle" style="color:#F59E0B;"></i><span style="color:#F59E0B;">Fair password - add more characters</span>';
    } else if (score === 3) {
      strengthLevel.classList.add("strong");
      strengthText.innerHTML =
        '<i class="fas fa-check-circle" style="color:#10B981;"></i><span style="color:#10B981;">Strong password!</span>';
    } else if (score === 4) {
      strengthLevel.classList.add("very-strong");
      strengthText.innerHTML =
        '<i class="fas fa-star" style="color:#34D399;"></i><span style="color:#34D399;">Very strong password!</span>';
    }
  }

  signupPassword.addEventListener("input", function () {
    checkPasswordStrength(this.value);
    checkPasswordMatch();
  });

  function checkPasswordMatch() {
    const password = signupPassword.value;
    const confirm = confirmPassword.value;

    if (confirm.length === 0) {
      passwordMatch.className = "password-match";
      passwordMatch.innerHTML = '<i class="fas fa-circle"></i><span>Confirm your password</span>';
      return;
    }

    if (password === confirm && password.length > 0) {
      passwordMatch.className = "password-match matched";
      passwordMatch.innerHTML = '<i class="fas fa-check-circle"></i><span>Passwords match</span>';
    } else {
      passwordMatch.className = "password-match error";
      passwordMatch.innerHTML = '<i class="fas fa-times-circle"></i><span>Passwords do not match</span>';
    }
  }

  confirmPassword.addEventListener("input", checkPasswordMatch);

  // ============ ROLE SELECTION ============
  const roleBtns = document.querySelectorAll(".role-btn");
  let selectedRole = "farmer";

  roleBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      roleBtns.forEach((b) => b.classList.remove("active"));
      this.classList.add("active");
      selectedRole = this.dataset.role;
    });
  });

  // ============ SIGNUP WITH EMAIL ============
  document.getElementById("submitSignup").addEventListener("click", async function () {
    const name = document.getElementById("signupName").value.trim();
    const email = document.getElementById("signupEmail").value.trim();
    const password = signupPassword.value;
    const confirm = confirmPassword.value;
    const agreeTerms = document.getElementById("agreeTerms").checked;

    // Validation
    if (!name) {
      showToast("Please enter your full name", "error");
      return;
    }

    if (!email || !email.includes("@") || !email.includes(".")) {
      showToast("Please enter a valid email address", "error");
      return;
    }

    if (password.length < 8) {
      showToast("Password must be at least 8 characters", "error");
      return;
    }

    if (password !== confirm) {
      showToast("Passwords do not match", "error");
      return;
    }

    if (!agreeTerms) {
      showToast("Please agree to the Terms of Service", "error");
      return;
    }

    // Show loading state
    const originalContent = this.innerHTML;
    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
    this.disabled = true;

    try {
      // Create user with Firebase
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Update profile with display name
      await updateProfile(user, {
        displayName: name
      });

      // Send email verification
      await sendEmailVerification(user);

      showToast("🎉 Account created successfully! Please verify your email.", "success");

      // Close modal
      closeModal(signupModal);

      setTimeout(() => {
        this.innerHTML = originalContent;
        this.disabled = false;
      }, 1000);

    } catch (error) {
      console.error("Signup error:", error);
      let errorMessage = "Signup failed. Please try again.";
      
      switch (error.code) {
        case 'auth/email-already-in-use':
          errorMessage = "This email is already registered. Please login.";
          break;
        case 'auth/invalid-email':
          errorMessage = "Invalid email address.";
          break;
        case 'auth/weak-password':
          errorMessage = "Password is too weak.";
          break;
        default:
          errorMessage = error.message || "Signup failed. Please try again.";
      }
      
      showToast(errorMessage, "error");
      this.innerHTML = originalContent;
      this.disabled = false;
    }
  });

  // ============ LOGIN WITH EMAIL ============
  document.getElementById("submitLogin").addEventListener("click", async function () {
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    if (!email) {
      showToast("Please enter your email", "error");
      return;
    }

    if (!password) {
      showToast("Please enter your password", "error");
      return;
    }

    // Show loading
    const originalContent = this.innerHTML;
    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
    this.disabled = true;

    try {
      await signInWithEmailAndPassword(auth, email, password);
      showToast("👋 Welcome back!", "success");
      closeModal(loginModal);
      
      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = "pages/dashboard.html";
      }, 1000);

    } catch (error) {
      console.error("Login error:", error);
      let errorMessage = "Invalid email or password";
      
      switch (error.code) {
        case 'auth/user-not-found':
          errorMessage = "No account found with this email.";
          break;
        case 'auth/wrong-password':
          errorMessage = "Incorrect password.";
          break;
        case 'auth/too-many-requests':
          errorMessage = "Too many attempts. Please try again later.";
          break;
        default:
          errorMessage = error.message || "Login failed. Please try again.";
      }
      
      showToast(errorMessage, "error");
      this.innerHTML = originalContent;
      this.disabled = false;
    }
  });

  // ============ GOOGLE LOGIN ============
  async function signInWithGoogle() {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const user = result.user;
      showToast("👋 Welcome " + (user.displayName || "User") + "!", "success");
      closeModal(loginModal);
      closeModal(signupModal);
      
      setTimeout(() => {
        window.location.href = "pages/dashboard.html";
      }, 1000);
    } catch (error) {
      console.error("Google sign-in error:", error);
      showToast(error.message || "Google sign-in failed", "error");
    }
  }

  document.getElementById("googleLoginBtn").addEventListener("click", signInWithGoogle);
  document.getElementById("googleSignupBtn").addEventListener("click", signInWithGoogle);

  // ============ GITHUB LOGIN ============
  async function signInWithGitHub() {
    try {
      const result = await signInWithPopup(auth, githubProvider);
      const user = result.user;
      showToast("👋 Welcome " + (user.displayName || "User") + "!", "success");
      closeModal(loginModal);
      closeModal(signupModal);
      
      setTimeout(() => {
        window.location.href = "pages/dashboard.html";
      }, 1000);
    } catch (error) {
      console.error("GitHub sign-in error:", error);
      showToast(error.message || "GitHub sign-in failed", "error");
    }
  }

  document.getElementById("githubLoginBtn").addEventListener("click", signInWithGitHub);
  document.getElementById("githubSignupBtn").addEventListener("click", signInWithGitHub);

  // ============ FORGOT PASSWORD ============
  document.getElementById("submitResetPassword").addEventListener("click", async function () {
    const email = document.getElementById("resetEmail").value.trim();

    if (!email) {
      showToast("Please enter your email address", "error");
      return;
    }

    // Show loading
    const originalContent = this.innerHTML;
    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    this.disabled = true;

    try {
      await sendPasswordResetEmail(auth, email);
      showToast("✅ Password reset link sent to your email!", "success");
      closeModal(forgotPasswordModal);
      document.getElementById("resetEmail").value = "";
      
      this.innerHTML = originalContent;
      this.disabled = false;
      
    } catch (error) {
      console.error("Reset password error:", error);
      let errorMessage = "Failed to send reset link";
      
      switch (error.code) {
        case 'auth/user-not-found':
          errorMessage = "No account found with this email.";
          break;
        case 'auth/invalid-email':
          errorMessage = "Invalid email address.";
          break;
        default:
          errorMessage = error.message || "Failed to send reset link. Please try again.";
      }
      
      showToast(errorMessage, "error");
      this.innerHTML = originalContent;
      this.disabled = false;
    }
  });

  // ============ LOGOUT ============
  document.getElementById("logoutBtn").addEventListener("click", async function () {
    try {
      await signOut(auth);
      showToast("Logged out successfully", "success");
      // Update UI will happen via onAuthStateChanged
    } catch (error) {
      console.error("Logout error:", error);
      showToast("Logout failed", "error");
    }
  });

  // ============ ENTER KEY SUPPORT ============
  document.getElementById("loginEmail").addEventListener("keypress", function (e) {
    if (e.key === "Enter") document.getElementById("loginPassword").focus();
  });

  document.getElementById("loginPassword").addEventListener("keypress", function (e) {
    if (e.key === "Enter") document.getElementById("submitLogin").click();
  });

  document.querySelectorAll("#signupModal .input-field").forEach((input, index, inputs) => {
    input.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        const next = inputs[index + 1];
        if (next) {
          next.focus();
        } else {
          document.getElementById("submitSignup").click();
        }
      }
    });
  });

  document.getElementById("resetEmail").addEventListener("keypress", function (e) {
    if (e.key === "Enter") document.getElementById("submitResetPassword").click();
  });

  // ============ MOBILE MENU ============
  let mobileMenuOpen = false;
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const navLinks = document.querySelector(".nav-links");

  mobileMenuBtn.onclick = () => {
    mobileMenuOpen = !mobileMenuOpen;
    if (mobileMenuOpen) {
      navLinks.style.display = "flex";
      navLinks.style.flexDirection = "column";
      navLinks.style.position = "absolute";
      navLinks.style.top = "70px";
      navLinks.style.left = "0";
      navLinks.style.right = "0";
      navLinks.style.background = "#1E293B";
      navLinks.style.padding = "1rem";
      navLinks.style.gap = "1rem";
    } else {
      navLinks.style.display = "none";
    }
  };

  // ============ SMOOTH SCROLL ============
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });

  console.log("🚀 Application initialized with Firebase Authentication");
});