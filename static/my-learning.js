(function () {
    "use strict";

    const loading = document.getElementById("learning-loading");
    const content = document.getElementById("learning-content");
    const errorBox = document.getElementById("learning-error");

    function addText(parent, tag, text, className) {
        const element = document.createElement(tag);
        element.textContent = text;
        if (className) element.className = className;
        parent.appendChild(element);
        return element;
    }

    function careerCard(career, subtitle) {
        const column = document.createElement("div");
        column.className = "col";
        const card = document.createElement("article");
        card.className = "learning-card";
        addText(card, "div", career.category, "small text-primary fw-semibold");
        addText(card, "h3", career.name, "h5 fw-bold mt-2");
        addText(card, "p", subtitle || career.description, "small text-muted");
        const link = document.createElement("a");
        link.className = "btn btn-sm btn-outline-primary";
        link.href = `/career?id=${encodeURIComponent(career.id)}`;
        link.textContent = "Open roadmap";
        card.appendChild(link);
        column.appendChild(card);
        return column;
    }

    function renderCareerList(targetId, emptyId, ids, careersById, subtitle) {
        const target = document.getElementById(targetId);
        target.replaceChildren();
        let count = 0;
        ids.forEach(function (id) {
            const career = careersById.get(Number(id));
            if (!career) return;
            target.appendChild(careerCard(career, subtitle));
            count += 1;
        });
        document.getElementById(emptyId).classList.toggle("d-none", count !== 0);
    }

    function renderProgress(state, careersById) {
        const target = document.getElementById("skill-progress");
        target.replaceChildren();
        let count = 0;
        Object.entries(state.completed_skills || {}).forEach(function ([careerId, skills]) {
            const career = careersById.get(Number(careerId));
            if (!career || !Array.isArray(skills) || !skills.length) return;
            count += 1;
            const section = document.createElement("section");
            section.className = "learning-card mb-3";
            const heading = document.createElement("div");
            heading.className = "d-flex justify-content-between align-items-center gap-2";
            addText(heading, "h3", career.name, "h6 fw-bold mb-0");
            const progress = document.createElement("span");
            const percent = Math.round((skills.length / Math.max(career.required_skills.length, 1)) * 100);
            progress.className = "small text-muted";
            progress.textContent = `${skills.length}/${career.required_skills.length} skills · ${percent}%`;
            heading.appendChild(progress);
            section.appendChild(heading);
            const bar = document.createElement("div");
            bar.className = "progress my-3";
            bar.setAttribute("role", "progressbar");
            bar.setAttribute("aria-label", `${career.name} skill progress`);
            bar.setAttribute("aria-valuenow", String(percent));
            bar.setAttribute("aria-valuemin", "0");
            bar.setAttribute("aria-valuemax", "100");
            const fill = document.createElement("div");
            fill.className = "progress-bar";
            fill.style.width = `${percent}%`;
            bar.appendChild(fill);
            section.append(bar, document.createTextNode(skills.join(" · ")));
            target.appendChild(section);
        });
        document.getElementById("progress-empty").classList.toggle("d-none", count !== 0);
    }

    function renderQuizResults(results, careersById) {
        const target = document.getElementById("saved-quiz-results");
        target.replaceChildren();
        const entries = Array.isArray(results) ? results.slice().reverse() : [];
        entries.forEach(function (result) {
            const column = document.createElement("div");
            column.className = "col";
            const card = document.createElement("article");
            card.className = "learning-card";
            const date = result.created_at ? new Date(result.created_at) : null;
            addText(card, "div", date && !Number.isNaN(date.valueOf()) ? `Saved ${date.toLocaleDateString()}` : "Saved quiz result", "small text-muted");
            addText(card, "h3", "Career ideas from your quiz", "h6 fw-bold mt-2");
            const list = document.createElement("ul");
            list.className = "small mb-0";
            (result.career_ids || []).forEach(function (id) {
                const career = careersById.get(Number(id));
                if (!career) return;
                const item = document.createElement("li");
                const link = document.createElement("a");
                link.href = `/career?id=${encodeURIComponent(career.id)}`;
                link.textContent = career.name;
                item.appendChild(link);
                list.appendChild(item);
            });
            card.appendChild(list);
            column.appendChild(card);
            target.appendChild(column);
        });
        document.getElementById("quiz-empty").classList.toggle("d-none", entries.length !== 0);
    }

    function showFailure(error, unauthorized) {
        loading.classList.add("d-none");
        errorBox.replaceChildren();
        addText(errorBox, "p", error, "mb-2");
        if (unauthorized) {
            const link = document.createElement("a");
            link.href = "/login";
            link.className = "alert-link";
            link.textContent = "Log in to view your saved learning.";
            errorBox.appendChild(link);
        }
        errorBox.classList.remove("d-none");
    }

    async function load() {
        try {
            const [stateResponse, catalogResponse] = await Promise.all([
                fetch("/api/v1/learning"),
                fetch("/api/v1/explore/careers")
            ]);
            if (stateResponse.status === 401 || stateResponse.status === 404) {
                showFailure("Your session is missing or expired.", true);
                return;
            }
            const [state, catalog] = await Promise.all([
                stateResponse.json(),
                catalogResponse.json()
            ]);
            if (!stateResponse.ok || !state.success) throw new Error(state.error || "Unable to load your saved learning.");
            if (!catalogResponse.ok || !catalog.success) throw new Error(catalog.error || "Unable to load career details.");
            const careersById = new Map(catalog.careers.map(function (career) { return [career.id, career]; }));
            renderCareerList("favorite-careers", "favorites-empty", state.favorites || [], careersById);
            renderCareerList("saved-roadmaps", "roadmaps-empty", state.saved_roadmaps || [], careersById, "Saved learning roadmap");
            renderProgress(state, careersById);
            renderQuizResults(state.quiz_results || [], careersById);
            loading.classList.add("d-none");
            content.classList.remove("d-none");
        } catch (error) {
            showFailure(error.message || "Unable to load your saved learning.", false);
        }
    }

    load();
})();
