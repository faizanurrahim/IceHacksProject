(function () {
    "use strict";

    const form = document.getElementById("career-quiz-form");
    const errorBox = document.getElementById("quiz-error");
    const resultsSection = document.getElementById("quiz-results");
    const recommendations = document.getElementById("quiz-recommendations");
    const saveButton = document.getElementById("save-quiz-result");
    const saveMessage = document.getElementById("save-result-message");
    let recommendedIds = [];

    function selectedValues(name) {
        return Array.from(document.querySelectorAll(`[data-options="${name}"] input:checked`))
            .map(function (input) { return input.value; });
    }

    function addText(parent, tag, text, className) {
        const element = document.createElement(tag);
        element.textContent = text;
        if (className) element.className = className;
        parent.appendChild(element);
        return element;
    }

    document.querySelectorAll("[data-options]").forEach(function (group) {
        group.addEventListener("change", function (event) {
            if (event.target.type !== "checkbox" || !event.target.checked) return;
            const max = group.dataset.options === "work_styles" ? 3 : 5;
            if (group.querySelectorAll("input:checked").length > max) {
                event.target.checked = false;
                errorBox.textContent = `Choose up to ${max} options in each group.`;
                errorBox.classList.remove("d-none");
            } else {
                errorBox.classList.add("d-none");
            }
        });
    });

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        errorBox.classList.add("d-none");
        saveMessage.textContent = "";
        const answers = {
            education: document.getElementById("education").value,
            subjects: selectedValues("subjects"),
            interests: selectedValues("interests"),
            skills: selectedValues("skills"),
            work_styles: selectedValues("work_styles")
        };
        const unanswered = ["subjects", "interests", "skills", "work_styles"]
            .filter(function (field) { return answers[field].length === 0; });
        if (!answers.education || unanswered.length) {
            errorBox.textContent = unanswered.length
                ? `Please choose at least one answer for: ${unanswered.join(", ").replaceAll("_", " ")}.`
                : "Please choose your current education level.";
            errorBox.classList.remove("d-none");
            return;
        }
        const submit = document.getElementById("quiz-submit");
        submit.disabled = true;
        submit.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Finding career ideas…';
        try {
            const response = await fetch("/api/v1/career-quiz", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(answers)
            });
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || "Unable to generate your career ideas.");
            recommendedIds = result.recommendations.map(function (item) { return item.id; });
            renderRecommendations(result.recommendations);
            resultsSection.classList.remove("d-none");
            resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        } catch (error) {
            errorBox.textContent = error.message || "Unable to generate recommendations. Please try again.";
            errorBox.classList.remove("d-none");
        } finally {
            submit.disabled = false;
            submit.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-2"></i>Show my career ideas';
        }
    });

    function renderRecommendations(items) {
        recommendations.replaceChildren();
        items.forEach(function (item) {
            const column = document.createElement("div");
            column.className = "col-12";
            const card = document.createElement("article");
            card.className = "result-card";
            const header = document.createElement("div");
            header.className = "d-flex justify-content-between align-items-start gap-3";
            const nameBlock = document.createElement("div");
            addText(nameBlock, "div", item.category || "Career path", "small text-primary fw-semibold");
            addText(nameBlock, "h3", item.name, "h5 fw-bold mt-1");
            const score = addText(header, "span", `${item.match_percentage}% match`, "badge rounded-pill text-bg-primary");
            score.setAttribute("aria-label", `Rule-based match score: ${item.match_percentage} percent`);
            header.prepend(nameBlock);
            card.appendChild(header);
            addText(card, "p", "These are transparent rule-based matches from your selected answers, not a prediction of success or job fit.", "small text-muted");
            addText(card, "h4", "Why it appeared", "h6 fw-bold");
            const reasons = document.createElement("ul");
            (item.reasons || []).forEach(function (reason) { addText(reasons, "li", reason); });
            card.appendChild(reasons);
            addText(card, "h4", "Skills to explore", "h6 fw-bold mt-3");
            addText(card, "p", (item.suggested_skills || []).join(" · "), "mb-3");
            const link = document.createElement("a");
            link.className = "btn btn-outline-primary btn-sm";
            link.href = `/career?id=${encodeURIComponent(item.id)}`;
            link.textContent = "Explore this roadmap";
            card.appendChild(link);
            column.appendChild(card);
            recommendations.appendChild(column);
        });
    }

    saveButton.addEventListener("click", async function () {
        if (!recommendedIds.length) return;
        saveButton.disabled = true;
        saveMessage.textContent = "";
        try {
            const response = await fetch("/api/v1/learning/quiz-results", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ career_ids: recommendedIds.slice(0, 5) })
            });
            const result = await response.json();
            if (!response.ok) {
                saveMessage.textContent = response.status === 401
                    ? "Log in to save quiz results. You can still explore these suggestions without an account."
                    : (result.error || "Unable to save these quiz results.");
                return;
            }
            saveMessage.textContent = "Quiz results saved to My Learning.";
        } catch {
            saveMessage.textContent = "Unable to reach CareerPath. Check your connection and try again.";
        } finally {
            saveButton.disabled = false;
        }
    });

    document.getElementById("retake-quiz").addEventListener("click", function () {
        resultsSection.classList.add("d-none");
        form.scrollIntoView({ behavior: "smooth", block: "start" });
    });
})();
