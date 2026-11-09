(function () {
    "use strict";

    const selection = document.getElementById("career-selection");
    const errorBox = document.getElementById("compare-error");
    const results = document.getElementById("comparison-results");
    const content = document.getElementById("comparison-content");
    const count = document.getElementById("compare-count");
    const selectionKey = "careerpath-compare-selection";
    let catalog = [];

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

    function readRequestedIds() {
        const query = new URLSearchParams(window.location.search).get("ids");
        let raw;
        try {
            raw = query ? query.split(",") : JSON.parse(localStorage.getItem(selectionKey) || "[]");
        } catch {
            raw = [];
        }
        return Array.isArray(raw) ? raw.map(Number).filter(Number.isInteger).slice(0, 4) : [];
    }

    function renderComparison(careers) {
        content.replaceChildren();
        const header = document.createElement("div");
        header.className = "row g-3";
        careers.forEach(function (career) {
            const column = document.createElement("div");
            column.className = "col-12 col-md";
            const card = document.createElement("article");
            card.className = "compare-career";
            addText(card, "div", career.category, "small text-primary fw-semibold");
            addText(card, "h3", career.name, "h5 fw-bold mt-2");
            const link = document.createElement("a");
            link.href = `/career?id=${encodeURIComponent(career.id)}`;
            link.className = "btn btn-sm btn-outline-primary";
            link.textContent = "View roadmap";
            card.appendChild(link);
            column.appendChild(card);
            header.appendChild(column);
        });
        content.appendChild(header);

        const fields = [
            ["Responsibilities", "responsibilities"],
            ["Education", "education"],
            ["Required skills", "required_skills"],
            ["Learning difficulty", "learning_difficulty"],
            ["Possible career paths", "career_paths"]
        ];
        fields.forEach(function ([label, key]) {
            const row = document.createElement("section");
            row.className = "comparison-row";
            addText(row, "h4", label, "h6 fw-bold");
            const columns = document.createElement("div");
            columns.className = "row g-3";
            careers.forEach(function (career) {
                const column = document.createElement("div");
                column.className = "col-12 col-md";
                const value = career[key];
                if (Array.isArray(value)) {
                    const list = document.createElement("ul");
                    list.className = "small mb-0";
                    value.forEach(function (item) { addText(list, "li", item); });
                    column.appendChild(list);
                } else {
                    addText(column, "p", value || "Not specified", "small mb-0");
                }
                columns.appendChild(column);
            });
            row.appendChild(columns);
            content.appendChild(row);
        });
        results.classList.remove("d-none");
    }

    async function loadCatalog() {
        try {
            const response = await fetch("/api/v1/explore/careers");
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || "Unable to load career list.");
            catalog = result.careers;
            catalog.forEach(function (career) {
                const option = document.createElement("option");
                option.value = career.id;
                option.textContent = `${career.name} — ${career.category}`;
                selection.appendChild(option);
            });
            const requested = new Set(readRequestedIds());
            Array.from(selection.options).forEach(function (option) {
                option.selected = requested.has(Number(option.value));
            });
            updateCount();
            if (requested.size >= 2) await compare();
        } catch (error) {
            showError(error.message || "Unable to load careers. Please try again.");
        }
    }

    function updateCount() {
        count.textContent = `${selection.selectedOptions.length} selected (choose 2 to 4)`;
    }

    async function compare() {
        errorBox.classList.add("d-none");
        const ids = Array.from(selection.selectedOptions).map(function (option) { return Number(option.value); });
        updateCount();
        if (ids.length < 2 || ids.length > 4) {
            showError("Select between two and four different careers.");
            results.classList.add("d-none");
            return;
        }
        try {
            const response = await fetch("/api/v1/careers/compare", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ career_ids: ids })
            });
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || "Unable to compare those careers.");
            localStorage.setItem(selectionKey, JSON.stringify(ids));
            renderComparison(result.careers);
        } catch (error) {
            showError(error.message || "Unable to compare careers. Please try again.");
        }
    }

    selection.addEventListener("change", function () {
        updateCount();
        if (selection.selectedOptions.length > 4) {
            selection.options[selection.selectedIndex].selected = false;
            updateCount();
            showError("Compare up to four careers at a time.");
        } else {
            errorBox.classList.add("d-none");
        }
    });
    document.getElementById("compare-button").addEventListener("click", compare);
    loadCatalog();
})();
