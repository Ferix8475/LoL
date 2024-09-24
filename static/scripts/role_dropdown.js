/* 
    Script to create the custom dropdown menu for the roles, retrieves the icons of the images along with the text per option 
*/
document.addEventListener("DOMContentLoaded", function() {
    const selectElement = document.getElementById("role-select");
    const selectedOptionElement = document.querySelector(".selected-option");
    const optionsContainer = document.querySelector(".options-container");

    function updateSelectedOption(value, icon, text) {
        const iconElement = selectedOptionElement.querySelector(".option-icon");
        const textElement = selectedOptionElement.querySelector(".option-text");
        iconElement.src = icon;
        iconElement.alt = text;
        textElement.textContent = text;
        selectElement.value = value;
    }

    function createOptionElement(option) {
        const value = option.value;
        const icon = option.getAttribute("data-icon");
        const text = option.textContent;
        const optionElement = document.createElement("div");
        optionElement.classList.add("option");
        optionElement.innerHTML = `<img src="${icon}" alt="${text}" class="option-icon"><span class="option-text">${text}</span>`;
        optionElement.addEventListener("click", function() {
            updateSelectedOption(value, icon, text);
            optionsContainer.style.display = "none";
        });
        return optionElement;
    }

    selectedOptionElement.addEventListener("click", function() {
        optionsContainer.style.display = optionsContainer.style.display === "block" ? "none" : "block";
    });

    Array.from(selectElement.options).forEach(option => {
        optionsContainer.appendChild(createOptionElement(option));
    });

    // Initialize with the first option
    const firstOption = selectElement.options[0];
    updateSelectedOption(firstOption.value, firstOption.getAttribute("data-icon"), firstOption.textContent);
});

