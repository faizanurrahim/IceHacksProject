(function () {
    "use strict";

    const grid = document.getElementById("career-grid");
    const search = document.getElementById("career-search");
    const category = document.getElementById("category-filter");
    const errorBox = document.getElementById("explorer-error");
    const count = document.getElementById("result-count");
    const selectedCount = document.getElementById("selected-count");
    const emptyState = document.getElementById("empty-state");
    const selectionKey = "careerpath-compare-selection";
    let selected = readSelection();
    let favorites = [];
    let searchTimer;

    function readSelection() {
        try {
            const value = JSON.parse(localStorage.getItem(selectionKey) || "[]");
            return Array.isArray(value) ? value.filter(Number.isInteger).slice(0, 4) : [];
        } catch {
            return [];
        }
    }

    function saveSelection() {
        localStorage.setItem(selectionKey, JSON.stringify(selected));
        selectedCount.textContent = String(selected.length);
    }

    function showError(message) {
        errorBox.textContent = message;
        errorBox.classList.remove("d-none");
    }

    function addText(parent, tag, text, className) {
        const element = document.createElement(tag);
        element.textContent = text;
        if (className) element.className = className;
        parent.appendChild(element);
        return element;
    }

    function showToast(message, success) {
        const host = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = `toast align-items-center ${success ? "text-bg-success" : "text-bg-danger"} border-0`;
        toast.setAttribute("role", "status");
        toast.innerHTML = '<div class="d-flex"><div class="toast-body"></div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>';
        toast.querySelector(".toast-body").textContent = message;
        host.appendChild(toast);
        const instance = new bootstrap.Toast(toast, { delay: 3200 });
        instance.show();
        toast.addEventListener("hidden.bs.toast", function () { toast.remove(); });
    }

    function renderCareer(career) {
        const column = document.createElement("div");
        column.className = "col";
        const card = document.createElement("article");
        card.className = "explore-card";
        const body = document.createElement("div");
        body.className = "card-body d-flex flex-column";
        addText(body, "div", career.category, "career-category");
        addText(body, "h2", career.name, "h5 fw-bold mt-2 mb-2");
        addText(body, "p", career.description, "text-muted");
        const skillWrap = document.createElement("div");
        skillWrap.className = "mb-3";
        (career.required_skills || []).slice(0, 4).forEach(function (skill) {
            addText(skillWrap, "span", skill, "career-skill");
        });
        body.appendChild(skillWrap);
        const actions = document.createElement("div");
        actions.className = "d-flex gap-2 mt-auto flex-wrap";
        const details = document.createElement("a");
        details.className = "btn btn-primary btn-sm";
        details.href = `/career?id=${encodeURIComponent(career.id)}`;
        details.textContent = "View roadmap";
        const compareLabel = document.createElement("label");
        compareLabel.className = "btn btn-outline-secondary btn-sm";
        const compareInput = document.createElement("input");
        compareInput.type = "checkbox";
        compareInput.className = "form-check-input me-1";
        compareInput.checked = selected.includes(career.id);
        compareInput.setAttribute("aria-label", `Select ${career.name} to compare`);
        compareInput.addEventListener("change", function () {
            if (compareInput.checked) {
                if (selected.length >= 4) {
                    compareInput.checked = false;
                    showToast("Compare up to four careers at a time.", false);
                    return;
                }
                selected.push(career.id);
            } else {
                selected = selected.filter(function (id) { return id !== career.id; });
            }
            saveSelection();
        });
        compareLabel.append(compareInput, document.createTextNode("Compare"));
        const favorite = document.createElement("button");
        favorite.type = "button";
        favorite.className = "btn btn-outline-secondary btn-sm";
        favorite.innerHTML = favorites.includes(career.id)
            ? '<i class="fa-solid fa-heart me-1" aria-hidden="true"></i>Saved'
            : '<i class="fa-regular fa-heart me-1" aria-hidden="true"></i>Favorite';
        favorite.setAttribute("aria-label", `${favorites.includes(career.id) ? "Remove" : "Save"} ${career.name} favorite`);
        favorite.addEventListener("click", async function () {
            favorite.disabled = true;
            try {
                const response = await fetch("/api/v1/learning/favorites", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ career_id: career.id, favorite: !favorites.includes(career.id) })
                });
                const result = await response.json();
                if (!response.ok) {
                    showToast(response.status === 401 ? "Log in to save favorite careers." : (result.error || "Could not save this favorite."), false);
                    return;
                }
                favorites = result.favorites;
                favorite.innerHTML = favorites.includes(career.id)
                    ? '<i class="fa-solid fa-heart me-1" aria-hidden="true"></i>Saved'
                    : '<i class="fa-regular fa-heart me-1" aria-hidden="true"></i>Favorite';
                favorite.setAttribute("aria-label", `${favorites.includes(career.id) ? "Remove" : "Save"} ${career.name} favorite`);
                showToast(favorites.includes(career.id) ? "Career saved to My Learning." : "Favorite removed.", true);
            } catch {
                showToast("Unable to reach CareerPath. Check your connection and try again.", false);
            } finally {
                favorite.disabled = false;
            }
        });
        actions.append(details, compareLabel, favorite);
        body.appendChild(actions);
        card.appendChild(body);
        column.appendChild(card);
        return column;
    }

    async function loadCareers() {
        errorBox.classList.add("d-none");
        count.textContent = "Loading careers…";
        try {
            const params = new URLSearchParams();
            if (search.value.trim()) params.set("search", search.value.trim());
            if (category.value) params.set("category", category.value);
            const response = await fetch(`/api/v1/explore/careers?${params.toString()}`);
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || "Unable to load careers.");
            const selectedCategory = category.value;
            if (!category.dataset.loaded) {
                result.categories.forEach(function (name) {
                    const option = document.createElement("option");
                    option.value = name;
                    option.textContent = name;
                    category.appendChild(option);
                });
                category.dataset.loaded = "true";
                category.value = selectedCategory;
            }
            grid.replaceChildren();
            result.careers.forEach(function (career) { grid.appendChild(renderCareer(career)); });
            count.textContent = `${result.careers.length} ${result.careers.length === 1 ? "career" : "careers"} found`;
            emptyState.classList.toggle("d-none", result.careers.length !== 0);
            saveSelection();
        } catch (error) {
            count.textContent = "";
            showError(error.message || "Unable to load careers. Please try again.");
        }
    }

    fetch("/api/v1/learning")
        .then(function (response) {
            if (response.status === 401 || response.status === 404) return null;
            if (!response.ok) throw new Error("Unable to load saved career data.");
            return response.json();
        })
        .then(function (result) {
            if (result) favorites = result.favorites || [];
            loadCareers();
        })
        .catch(function (error) {
            showError(error.message || "Unable to load saved career data.");
            loadCareers();
        });

    search.addEventListener("input", function () {
        window.clearTimeout(searchTimer);
        searchTimer = window.setTimeout(loadCareers, 180);
    });
    category.addEventListener("change", loadCareers);
    document.getElementById("compare-selected").addEventListener("click", function (event) {
        if (selected.length < 2) {
            event.preventDefault();
            showToast("Select at least two careers to compare.", false);
            return;
        }
        event.currentTarget.href = `/compare?ids=${selected.join(",")}`;
    });
    saveSelection();
})();
