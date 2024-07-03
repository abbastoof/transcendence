function generateStars(containerSelector, numberOfStars) {
    const starsContainer = document.querySelector(containerSelector);
    for (let index = 0; index < numberOfStars; index++) {
        const starDiv = document.createElement('div');
        starDiv.className = 'star';
        starsContainer.appendChild(starDiv);
    }
}