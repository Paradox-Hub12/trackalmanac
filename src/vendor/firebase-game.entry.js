export { initializeApp } from "firebase/app";
export { getAuth, GoogleAuthProvider, EmailAuthProvider, signInWithPopup, signInWithRedirect, getRedirectResult, signInAnonymously,
  createUserWithEmailAndPassword, signInWithEmailAndPassword, sendEmailVerification, sendPasswordResetEmail,
  linkWithPopup, linkWithCredential, reauthenticateWithPopup, reauthenticateWithCredential, reload,
  onAuthStateChanged, signOut, deleteUser, browserLocalPersistence, setPersistence, connectAuthEmulator } from "firebase/auth";
export { getFirestore, doc, getDoc, setDoc, updateDoc, deleteDoc, writeBatch, collection, query, where, getDocs, arrayUnion, arrayRemove,
  serverTimestamp, Timestamp, documentId, connectFirestoreEmulator } from "firebase/firestore/lite";
