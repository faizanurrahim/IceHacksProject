(function () {
    const preferenceKey = "careerpath-theme";
    const savedTheme = localStorage.getItem(preferenceKey);
    const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";

    function applyTheme(theme) {
        if (theme === "system") {
            theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        document.documentElement.dataset.theme = theme;
        const toggle = document.getElementById("careerpathThemeToggle");
        if (toggle) {
            toggle.innerHTML = theme === "dark"
                ? '<i class="fa-solid fa-sun" aria-hidden="true"></i>'
                : '<i class="fa-solid fa-moon" aria-hidden="true"></i>';
            toggle.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} theme`);
            toggle.title = `Switch to ${theme === "dark" ? "light" : "dark"} theme`;
        }
    }

    window.careerpathSetTheme = function (theme) {
        if (theme === "system") localStorage.removeItem(preferenceKey);
        else localStorage.setItem(preferenceKey, theme);
        applyTheme(theme === "system" ? systemTheme : theme);
    };

    applyTheme(savedTheme || systemTheme);

    document.addEventListener("DOMContentLoaded", function () {
        const host = document.querySelector("nav .container") || document.querySelector(".sidebar");
        if (!host) return;
        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.id = "careerpathThemeToggle";
        toggle.className = "careerpath-theme-toggle";
        toggle.setAttribute("aria-label", "Switch theme");
        host.appendChild(toggle);
        applyTheme(document.documentElement.dataset.theme);
        toggle.addEventListener("click", function () {
            const theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            localStorage.setItem(preferenceKey, theme);
            applyTheme(theme);
        });
    });
})();
