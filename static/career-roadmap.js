(function () {
    "use strict";

    const careerId = Number(new URLSearchParams(window.location.search).get("id"));
    const errorBox = document.getElementById("career-error");
    const loading = document.getElementById("career-loading");
    const content = document.getElementById("career-content");
    const message = document.getElementById("learning-message");
    let career;
    let favorites = [];
    let savedRoadmaps = [];
    let completedSkills = [];
    let signedIn = false;

    function addText(parent, tag, text, className) {
        const element = document.createElement(tag);
        element.textContent = text;
        if (className) element.className = className;
        parent.appendChild(element);
        return element;
    }

    function addList(targetId, values) {
        const list = document.getElementById(targetId);
        list.replaceChildren();
        (values || []).forEach(function (value) { addText(list, "li", value); });
    }

    function renderResources(target, resources) {
        target.replaceChildren();
        resources.forEach(function (resource) {
            const item = document.createElement("p");
            item.className = "mb-3";
            const link = document.createElement("a");
            link.className = "resource-link fw-semibold";
            link.href = resource.url;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = resource.title;
            item.append(link, document.createTextNode(` — ${resource.provider}. Covers: ${(resource.skills || []).join(", ")}.`));
            target.appendChild(item);
        });
    }

    function updateProgress() {
        const total = career.required_skills.length;
        const done = completedSkills.length;
        const percent = total ? Math.round((done / total) * 100) : 0;
        const bar = document.getElementById("skill-progress-bar");
        bar.style.width = `${percent}%`;
        bar.setAttribute("aria-valuenow", String(percent));
        document.getElementById("progress-count").textContent = `${done} of ${total} skills explored (${percent}%)`;
    }

    function renderSkills() {
        const host = document.getElementById("skill-list");
        host.replaceChildren();
        career.required_skills.forEach(function (skill) {
            const label = document.createElement("label");
            label.className = "skill-pill";
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.className = "form-check-input me-2";
            checkbox.checked = completedSkills.includes(skill);
            checkbox.setAttribute("aria-label", `Mark ${skill} as learned`);
            checkbox.addEventListener("change", async function () {
                checkbox.disabled = true;
                try {
                    const response = await fetch("/api/v1/learning/progress", {
                        method: "PUT",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ career_id: career.id, skill, completed: checkbox.checked })
                    });
                    const result = await response.json();
                    if (!response.ok) {
                        checkbox.checked = !checkbox.checked;
                        message.textContent = response.status === 401
                            ? "Log in to track skill progress. Your roadmap remains available without an account."
                            : (result.error || "Unable to save skill progress.");
                        return;
                    }
                    completedSkills = result.completed_skills[String(career.id)] || [];
                    updateProgress();
                    message.textContent = "Skill progress saved.";
                } catch {
                    checkbox.checked = !checkbox.checked;
                    message.textContent = "Unable to reach CareerPath. Check your connection and try again.";
                } finally {
                    checkbox.disabled = false;
                }
            });
            label.append(checkbox, document.createTextNode(skill));
            host.appendChild(label);
        });
        updateProgress();
    }

    function renderStages() {
        const host = document.getElementById("roadmap-stages");
        host.replaceChildren();
        career.roadmap.forEach(function (stage) {
            const column = document.createElement("div");
            column.className = "col";
            const card = document.createElement("article");
            card.className = "stage-card";
            addText(card, "div", stage.level, "small text-primary fw-bold text-uppercase");
            addText(card, "h3", stage.title, "h5 fw-bold mt-2");
            const learn = document.createElement("ul");
            learn.className = "small";
            stage.learn.forEach(function (item) { addText(learn, "li", item); });
            card.appendChild(learn);
            addText(card, "h4", "Practice project", "h6 fw-bold mt-3");
            addText(card, "p", stage.project, "small");
            addText(card, "h4", "Free resources", "h6 fw-bold");
            renderResources(card, stage.resources || []);
            column.appendChild(card);
            host.appendChild(column);
        });
    }

    function renderCareer() {
        document.title = `${career.name} Roadmap · CareerPath`;
        document.getElementById("career-name").textContent = career.name;
        document.getElementById("career-category").textContent = career.category;
        document.getElementById("career-description").textContent = career.description;
        document.getElementById("career-education").textContent = career.education;
        document.getElementById("career-difficulty").textContent = career.learning_difficulty;
        addList("responsibilities", career.responsibilities);
        addList("career-paths", career.career_paths);
        addList("career-next-steps", career.next_steps);
        addList("career-projects", career.projects);
        renderResources(document.getElementById("career-resources"), career.resources);
        renderSkills();
        renderStages();
        document.getElementById("favorite-career").innerHTML = favorites.includes(career.id)
            ? '<i class="fa-solid fa-heart me-2" aria-hidden="true"></i>Saved favorite'
            : '<i class="fa-regular fa-heart me-2" aria-hidden="true"></i>Save favorite';
        document.getElementById("save-roadmap").innerHTML = savedRoadmaps.includes(career.id)
            ? '<i class="fa-solid fa-bookmark me-2" aria-hidden="true"></i>Roadmap saved'
            : '<i class="fa-regular fa-bookmark me-2" aria-hidden="true"></i>Save roadmap';
        document.getElementById("account-hint").textContent = signedIn
            ? "Your saved items and checked skills are attached to your account."
            : "This roadmap is public. Log in to save it and track your progress.";
        loading.classList.add("d-none");
        content.classList.remove("d-none");
    }

    async function saveToggle(endpoint, key, currentValues, button, label) {
        if (!signedIn) {
            message.textContent = "Log in to save careers and track learning progress. The roadmap is available without an account.";
            return;
        }
        const saved = currentValues.includes(career.id);
        button.disabled = true;
        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ career_id: career.id, [key]: !saved })
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || `Unable to update ${label}.`);
            if (key === "favorite") favorites = result.favorites;
            else savedRoadmaps = result.saved_roadmaps;
            button.innerHTML = key === "favorite"
                ? (favorites.includes(career.id)
                    ? '<i class="fa-solid fa-heart me-2" aria-hidden="true"></i>Saved favorite'
                    : '<i class="fa-regular fa-heart me-2" aria-hidden="true"></i>Save favorite')
                : (savedRoadmaps.includes(career.id)
                    ? '<i class="fa-solid fa-bookmark me-2" aria-hidden="true"></i>Roadmap saved'
                    : '<i class="fa-regular fa-bookmark me-2" aria-hidden="true"></i>Save roadmap');
            message.textContent = `${label} ${saved ? "removed" : "saved"}.`;
        } catch (error) {
            message.textContent = error.message || `Unable to save ${label}.`;
        } finally {
            button.disabled = false;
        }
    }

    document.getElementById("favorite-career").addEventListener("click", function () {
        saveToggle("/api/v1/learning/favorites", "favorite", favorites, this, "Favorite");
    });
    document.getElementById("save-roadmap").addEventListener("click", function () {
        saveToggle("/api/v1/learning/roadmaps", "saved", savedRoadmaps, this, "Roadmap");
    });

    async function load() {
        if (!Number.isInteger(careerId) || careerId < 1) {
            loading.classList.add("d-none");
            errorBox.textContent = "This career link is missing a valid career ID. Return to the explorer and choose a career.";
            errorBox.classList.remove("d-none");
            return;
        }
        try {
            const response = await fetch(`/api/v1/career/${careerId}/roadmap`);
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || "Unable to load this career roadmap.");
            career = result.career;
            try {
                const stateResponse = await fetch("/api/v1/learning");
                if (stateResponse.ok) {
                    const state = await stateResponse.json();
                    signedIn = true;
                    favorites = state.favorites || [];
                    savedRoadmaps = state.saved_roadmaps || [];
                    completedSkills = (state.completed_skills || {})[String(career.id)] || [];
                } else if (stateResponse.status !== 401) {
                    message.textContent = "Could not load saved learning state. Your public career roadmap is still available.";
                }
            } catch {
                message.textContent = "Could not load saved learning state. Your public career roadmap is still available.";
            }
            renderCareer();
        } catch (error) {
            loading.classList.add("d-none");
            errorBox.textContent = error.message || "Unable to load this career roadmap.";
            errorBox.classList.remove("d-none");
        }
    }

    load();
})();
