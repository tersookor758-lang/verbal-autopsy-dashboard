document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.getElementById("mobileMenu");
    const header = document.querySelector(".site-header");

    if (!menuButton || !header) {
        return;
    }

    const toggleMenu = () => {
        header.classList.toggle("menu-open");
        menuButton.classList.toggle("active");

        menuButton.setAttribute(
            "aria-expanded",
            header.classList.contains("menu-open")
        );
    };

    menuButton.setAttribute("aria-expanded", "false");
    menuButton.addEventListener("click", toggleMenu);

    document.querySelectorAll(
        ".nav-links a, .nav-actions a"
    ).forEach(link => {
        link.addEventListener("click", () => {
            header.classList.remove("menu-open");
            menuButton.classList.remove("active");
            menuButton.setAttribute("aria-expanded", "false");
        });
    });

    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener("click", event => {
            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") {
                return;
            }

            const target = document.querySelector(targetId);

            if (!target) {
                return;
            }

            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });
    });
});