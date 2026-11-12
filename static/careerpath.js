(function () {
    const preferenceKey = "careerpath-theme";
    const themes = ["light", "dark", "special"];
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const savedTheme = localStorage.getItem(preferenceKey);

    function resolvedTheme(theme) {
        return theme === "system" ? (mediaQuery.matches ? "dark" : "light") : theme;
    }

    function applyTheme(theme) {
        const selectedTheme = themes.includes(theme) ? theme : "system";
        theme = resolvedTheme(selectedTheme);
        document.documentElement.dataset.theme = theme;
        document.documentElement.dataset.themePreference = selectedTheme;
        const toggle = document.getElementById("careerpathThemeToggle");
        if (toggle) {
            const nextTheme = themes[(themes.indexOf(theme) + 1) % themes.length];
            const labels = {
                light: "Light: white and purple",
                dark: "Dark: black and blue",
                special: "Special edition: dark blue and purple"
            };
            const icons = {
                light: "fa-sun",
                dark: "fa-moon",
                special: "fa-wand-magic-sparkles"
            };
            toggle.innerHTML = `<i class="fa-solid ${icons[theme]}" aria-hidden="true"></i>`;
            toggle.setAttribute("aria-label", `${labels[theme]}. Switch to ${labels[nextTheme]}`);
            toggle.title = `Current: ${labels[theme]}. Next: ${labels[nextTheme]}`;
        }
    }

    window.careerpathSetTheme = function (theme) {
        const selectedTheme = themes.includes(theme) ? theme : "system";
        if (selectedTheme === "system") localStorage.removeItem(preferenceKey);
        else localStorage.setItem(preferenceKey, selectedTheme);
        applyTheme(selectedTheme);
    };

    applyTheme(savedTheme || "system");

    document.addEventListener("DOMContentLoaded", function () {
        const host = document.querySelector("nav .container") || document.querySelector(".sidebar");
        if (!host) return;
        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.id = "careerpathThemeToggle";
        toggle.className = "careerpath-theme-toggle";
        toggle.setAttribute("aria-label", "Switch theme");
        host.appendChild(toggle);
        applyTheme(localStorage.getItem(preferenceKey) || "system");
        toggle.addEventListener("click", function () {
            const currentTheme = document.documentElement.dataset.theme;
            const nextTheme = themes[(themes.indexOf(currentTheme) + 1) % themes.length];
            window.careerpathSetTheme(nextTheme);
        });
    });

    mediaQuery.addEventListener("change", function () {
        if (!localStorage.getItem(preferenceKey)) applyTheme("system");
    });
})();
