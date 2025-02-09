// Import du module xrpl
const xrpl = require("xrpl");

// Fonction principale pour générer un portefeuille
async function generateWallet() {
  // Connexion au testnet de XRPL
  const client = new xrpl.Client("wss://s.altnet.rippletest.net:51233");
  console.log("Connecting to XRPL Testnet...");
  await client.connect();

  // Génération d'un portefeuille aléatoire
  const wallet = xrpl.Wallet.generate();

  // Affiche l'adresse et le secret du portefeuille
  console.log("Wallet generated!");
  console.log("Address:", wallet.classicAddress);
  console.log("Secret:", wallet.seed);

  // Déconnexion du client XRPL
  await client.disconnect();
}

// Exécute la fonction
generateWallet().catch(console.error);

import jsQR from "jsqr";

try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    console.log("Camera access granted.");
    video.srcObject = stream;
} catch (error) {
    console.error("Error accessing camera:", error);
    alert("Could not access camera. Please check permissions.");
}

const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });

async function scanQRCode() {
    const video = document.getElementById('camera');

    try {
        console.log("Requesting camera access...");
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        console.log("Camera stream started.");
        video.srcObject = stream;
    } catch (error) {
        console.error("Error accessing camera:", error);
        alert("Could not access camera. Please check permissions.");
    }
}

console.log("Captured frame:", imageData);
const code = jsQR(imageData.data, imageData.width, imageData.height);
if (code) {
    console.log("QR Code detected:", code.data);
}
