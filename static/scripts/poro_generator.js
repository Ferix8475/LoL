/*
    Script to dyanmically load images from the static/images/general/poro/ folder (images of poros) and to randomly select an image fro this set 
*/

document.addEventListener("DOMContentLoaded", function() {
    const imageFolder = 'general/poro/'; 
    const endpoint = `/api/images?folder=${imageFolder}`;

    // Function to get random image
    function getRandomImage(images) {
        const randomIndex = Math.floor(Math.random() * images.length);
        return images[randomIndex];
    }

    // Function to set random image
    function setRandomImage(imgElement, images) {
        const randomImage = getRandomImage(images);
        imgElement.src = `/static/images/${imageFolder}${randomImage}`;
    }

    // Fetch images from the server
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error fetching images:", data.error);
            } else {
                const imgElements = document.querySelectorAll('img.random-poro-image');
                imgElements.forEach(img => setRandomImage(img, data));
            }
        })
        .catch(error => console.error("Error:", error));
});
