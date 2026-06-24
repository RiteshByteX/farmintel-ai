// firebase-config.js
// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { 
  getAuth, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  GithubAuthProvider,
  sendPasswordResetEmail,
  onAuthStateChanged,
  signOut,
  updateProfile,
  sendEmailVerification
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// Your web app's Firebase configuration
// ✅ USING YOUR ACTUAL FIREBASE CONFIG
const firebaseConfig = {
  apiKey: "AIzaSyAR87p61Oawilfb014TbrUOet3KIfe-x_o",
  authDomain: "farmintel-ai.firebaseapp.com",
  projectId: "farmintel-ai",
  storageBucket: "farmintel-ai.firebasestorage.app",
  messagingSenderId: "534174863827",
  appId: "1:534174863827:web:6d6c866eeb394f6bc65f26",
  measurementId: "G-SNFKVWHGM3"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Providers
const googleProvider = new GoogleAuthProvider();
const githubProvider = new GithubAuthProvider();

// Export auth functions
export {
  auth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  GithubAuthProvider,
  sendPasswordResetEmail,
  onAuthStateChanged,
  signOut,
  updateProfile,
  sendEmailVerification,
  googleProvider,
  githubProvider
};