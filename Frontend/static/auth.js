// 🔥 Firebase imports
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getIdToken } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  signOut
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyD5ePko-KzkFKSo7Kfv01XeeCEHLRErquU",
  authDomain: "interviewflow-f23b4.firebaseapp.com",
  projectId: "interviewflow-f23b4",
  storageBucket: "interviewflow-f23b4.firebasestorage.app",
  messagingSenderId: "595080516204",
  appId: "1:595080516204:web:0b9e5bdf27f4525729be49"
};

// Init
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

/* ---------- GOOGLE AUTH ---------- */

window.loginWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    await sendTokenToBackend(result.user);
    // Don't redirect here - sendTokenToBackend handles it
  } catch (err) {
    if (
      err.code === "auth/popup-closed-by-user" ||
      err.code === "auth/cancelled-popup-request"
    ) return;

    console.error(err);
  }
};

window.signupWithGoogle = window.loginWithGoogle;

/* ---------- EMAIL AUTH ---------- */

window.loginWithEmail = async (event) => {
  if (event) event.preventDefault();
  
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const result = await signInWithEmailAndPassword(auth, email, password);
    await sendTokenToBackend(result.user);
    window.location.href = "/interview_section";
  } catch (err) {
    alert(err.message);
  }
};

window.signupWithEmail = async (event) => {
  if (event) event.preventDefault();
  
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    await sendTokenToBackend(result.user);
    window.location.href = "/interview_section";
  } catch (err) {
    alert(err.message);
  }
};

/* ---------- AUTH STATE ---------- */

onAuthStateChanged(auth, (user) => {
  console.log(user ? "Logged in" : "Not logged in");
});


// Flask session
async function sendTokenToBackend(user) {
  const token = await getIdToken(user);

  await fetch("/session_login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token })
  });

  // Wait a bit for Firebase auth to persist, then redirect
  setTimeout(() => {
    window.location.href = "/interview_section";
  }, 500);
}
