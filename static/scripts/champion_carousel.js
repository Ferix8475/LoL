document.addEventListener("DOMContentLoaded", function() {
    const imageFolder = 'champions/'; 
    const endpoint = `/api/images?folder=${imageFolder}`;
    const carouselContainer = document.getElementById('champion-carousel-images');

    // Fetch images from the server
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error fetching images:", data.error);
            } else {
                data.forEach(file => {
                    const img = document.createElement('img');
                    img.src = `/static/images/${imageFolder}${file}`;
                    img.alt = file.replace(/\.[^/.]+$/, ""); 
                    carouselContainer.appendChild(img);
                });

                data.forEach(file => {
                    const img = document.createElement('img');
                    img.src = `/static/images/${imageFolder}${file}`;
                    img.alt = file.replace(/\.[^/.]+$/, ""); 
                    carouselContainer.appendChild(img);
                });
            }
        })
        .catch(error => console.error("Error:", error));
});