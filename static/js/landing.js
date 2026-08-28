document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.getElementById("mobileMenu");
    const navLinks = document.querySelector(".nav-links");
    const navActions = document.querySelector(".nav-actions");

    if (menuButton && navLinks && navActions) {
        menuButton.addEventListener("click", () => {
            navLinks.classList.toggle("mobile-open");
            navActions.classList.toggle("mobile-open");
            menuButton.classList.toggle("active");
        });

        document.querySelectorAll(".nav-links a, .nav-actions a").forEach(link => {
            link.addEventListener("click", () => {
                navLinks.classList.remove("mobile-open");
                navActions.classList.remove("mobile-open");
                menuButton.classList.remove("active");
            });
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener("click", event => {
            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") {
                return;
            }

            const target = document.querySelector(targetId);

            if (target) {
                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });
});