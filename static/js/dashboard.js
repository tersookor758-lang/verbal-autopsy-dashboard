document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");

    function getCurrentTheme() {
        return document.documentElement.getAttribute("data-theme") || "light";
    }

    function updateThemeIcon(theme) {

        if (!themeIcon) {
            return;
        }

        if (theme === "dark") {

            themeIcon.classList.remove("bi-moon-fill");
            themeIcon.classList.add("bi-sun-fill");

        } else {

            themeIcon.classList.remove("bi-sun-fill");
            themeIcon.classList.add("bi-moon-fill");

        }
    }


    function applyTheme(theme) {

        document.documentElement.setAttribute(
            "data-theme",
            theme
        );

        localStorage.setItem(
            "theme",
            theme
        );

        updateThemeIcon(theme);
    }


    // Initialise theme

    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark" || savedTheme === "light") {

        applyTheme(savedTheme);

    } else {

        applyTheme("light");

    }


    // Toggle theme

    if (themeToggle) {

        themeToggle.addEventListener("click", function () {

            const currentTheme = getCurrentTheme();

            const newTheme =
                currentTheme === "dark"
                    ? "light"
                    : "dark";

            applyTheme(newTheme);

        });

    }


    // Allow elements elsewhere in the dashboard
    // to request a theme refresh.

    window.addEventListener("storage", function (event) {

        if (event.key === "theme") {

            const theme =
                event.newValue === "dark"
                    ? "dark"
                    : "light";

            applyTheme(theme);

        }

    });

});