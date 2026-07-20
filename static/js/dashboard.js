document.addEventListener("DOMContentLoaded", () => {

    const stateSelect = document.getElementById("state-select");
    const lgaSelect = document.getElementById("lga-select");

    if (!stateSelect || !lgaSelect || !window.allLgas) {
        return;
    }

    function populateLgas(selectedState, selectedLga = "") {

        lgaSelect.innerHTML = "";

        const defaultOption = document.createElement("option");
        defaultOption.value = "";

        if (!selectedState) {

            defaultOption.textContent = "Select a State First";

            lgaSelect.appendChild(defaultOption);

            lgaSelect.disabled = true;

            return;
        }

        defaultOption.textContent = "All LGAs";
        lgaSelect.appendChild(defaultOption);

        const lgas = window.allLgas[selectedState] || [];

        lgas.forEach((lga) => {

            const option = document.createElement("option");

            option.value = lga;
            option.textContent = lga;

            if (lga === selectedLga) {
                option.selected = true;
            }

            lgaSelect.appendChild(option);

        });

        lgaSelect.disabled = false;
    }

    populateLgas(
        stateSelect.value,
        lgaSelect.value
    );

    stateSelect.addEventListener("change", () => {

        populateLgas(
            stateSelect.value
        );

    });

});