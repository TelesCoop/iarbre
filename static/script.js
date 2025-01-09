// Sélectionne l'élément contenant l'image de fond
const fullscreenSection = document.querySelector(".fullscreen");

// Variable pour stocker l'intervalle de création de symboles "×"
let pixelInterval;

// Fonction pour créer et afficher le symbole "×" en vert foncé
function showSymbol(x, y) {
  const symbol = document.createElement("div");
  symbol.textContent = "×"; // Affiche le symbole "×"
  symbol.style.color = "#32412D"; // Vert foncé

  // Dimension aléatoire entre 10 et 100 pixels
  const randomSize = Math.floor(Math.random() * 91) + 10; // Génère un nombre entre 10 et 100
  symbol.style.fontSize = `${randomSize}px`; // Applique la taille aléatoire

  symbol.style.position = "absolute";
  symbol.style.top = `${y - randomSize / 2}px`; // Centrer verticalement
  symbol.style.left = `${x - randomSize / 2}px`; // Centrer horizontalement
  symbol.style.pointerEvents = "none";
  symbol.style.transition = "opacity 1s"; // Transition pour disparition douce

  fullscreenSection.appendChild(symbol);

  // Disparition du symbole après 1 seconde
  setTimeout(() => {
    symbol.style.opacity = "0"; // Rend le symbole transparent
    setTimeout(() => {
      symbol.remove(); // Supprime le symbole du DOM
    }, 1000);
  }, 1000);
}

// Fonction pour démarrer la génération continue de symboles "×" lors du dessin
function startSymbolGeneration(event) {
  const rect = fullscreenSection.getBoundingClientRect();

  // Crée un symbole initialement à la position actuelle de la souris ou du toucher
  createSymbol(event, rect);

  // Démarre un intervalle pour créer des symboles continus
  pixelInterval = setInterval(() => createSymbol(event, rect), 100);
}

// Fonction pour créer un symbole "×" à l'emplacement actuel de la souris ou du toucher
function createSymbol(event, rect) {
  let x, y;
  if (event.type === "mousemove" || event.type === "mouseup") {
    x = event.clientX - rect.left;
    y = event.clientY - rect.top;
  } else if (event.type === "touchmove" || event.type === "touchstart") {
    x = event.touches[0].clientX - rect.left;
    y = event.touches[0].clientY - rect.top;
  }
  showSymbol(x, y);
}

// Fonction pour arrêter la génération continue de symboles
function stopSymbolGeneration() {
  clearInterval(pixelInterval);
}

// Événements pour commencer et arrêter le maintien du clic/toucher
fullscreenSection.addEventListener("mouseup", startSymbolGeneration);
fullscreenSection.addEventListener("touchstart", startSymbolGeneration);

window.addEventListener("mouseup", stopSymbolGeneration);
window.addEventListener("touchend", stopSymbolGeneration);
