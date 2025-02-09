function calculateColor(score) {
    const red = Math.round(255 * (1-score/100));
    const green = Math.round(200*score/100);
    return `rgb(${red}, ${green}, 0)`;
}

function updateScoreColors() {
    const scoreElements = document.querySelectorAll('.color_by_score');
    scoreElements.forEach(scoreElement => {
        const scoreValue = scoreElement.querySelector('.scoreValue');
        const score = parseInt(scoreValue.textContent);
        const color = calculateColor(score);
        console.log(color);
        scoreElement.style.color = color;
    });
}