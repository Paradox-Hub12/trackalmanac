export { initializeApp } from "firebase/app";
export { getAuth, GoogleAuthProvider, signInWithPopup, signInWithRedirect, getRedirectResult, sendSignInLinkToEmail, isSignInWithEmailLink, signInWithEmailLink,
  onAuthStateChanged, signOut, deleteUser, reauthenticateWithPopup, browserLocalPersistence, setPersistence, connectAuthEmulator } from "firebase/auth";
export { getFirestore, doc, getDoc, setDoc, updateDoc, deleteDoc, writeBatch, collection, query, where, getDocs, arrayUnion, arrayRemove,
  serverTimestamp, Timestamp, documentId, connectFirestoreEmulator } from "firebase/firestore/lite";
