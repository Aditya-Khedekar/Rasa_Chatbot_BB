
 function createStarRating(sendCallback) {
  const container = document.createElement("div");
  container.className = "rating-container";
  container.innerHTML = `
    <div class="botMsg" style="margin-top: 10px;">
      <div class="stars" id="star-container">
        ${[1, 2, 3, 4, 5].map(i => `
        <div class="star-wrapper">
      <span class="star" data-value="${i}">&#9733;</span>
    <div class="star-label">${i}</div>
  </div>
`).join("")}

      </div>
    </div>
  `;
    // Inject star styles only once
  if (!document.getElementById("star-rating-style")) {
    const style = document.createElement("style");
    style.id = "star-rating-style";
    style.textContent = `
      .rating-container .stars {
      display: flex;
      justify-content: start;
      gap: 8px;
      font-size: 32px;
      padding: 8px 0;
      cursor: pointer;
      color: #ccc;
      transition: color 0.3s ease;
    }

    .rating-container .star {
      transition: transform 0.2s, color 0.2s;
    }

    .rating-container .star:hover {
      transform: scale(1.2);
      color: gold;
    }

    .rating-container .star.selected {
      color: gold;
    }
    
    .rating-container .star-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .rating-container .star-label {
      font-size: 14px;
      color: #888;
      margin-top: 2px;
    }
    `;
    document.head.appendChild(style);
  }

  const stars = container.querySelectorAll(".star");
  stars.forEach((star, index) => {
    star.addEventListener("click", () => {
      stars.forEach((s, i) => {
        s.classList.toggle("selected", i <= index);
      });
      const rating = index + 1;
      showBotTyping()
      if (sendCallback) sendCallback(rating);
    });
  });

  return container;
}

window.createStarRating = createStarRating;
