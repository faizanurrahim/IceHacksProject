(function () {
    "use strict";

    const form = document.getElementById("career-quiz-form");
    const errorBox = document.getElementById("quiz-error");
    const resultsSection = document.getElementById("quiz-results");
    const recommendations = document.getElementById("quiz-recommendations");
    const countryGuidance = document.getElementById("country-guidance");
    const saveButton = document.getElementById("save-quiz-result");
    const saveMessage = document.getElementById("save-result-message");
    const feedbackForm = document.getElementById("recommendation-feedback-form");
    const feedbackMessage = document.getElementById("recommendation-feedback-message");
    const followUpPanel = document.getElementById("follow-up-panel");
    let quizAnswers = null;
    let feedbackSubmissionId = null;
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

    async function loadCareerOptions() {
        const select = document.getElementById("preferred-career");
        const alternateSelect = document.getElementById("feedback-alternate-career");
        try {
            const response = await fetch("/api/v1/careers");
            const result = await response.json();
            if (!response.ok || !result || typeof result !== "object") {
                throw new Error("Unable to load dream-career options.");
            }
            Object.entries(result).forEach(function (entry) {
                const name = entry[0];
                const careerId = entry[1];
                const option = document.createElement("option");
                option.value = name;
                option.textContent = name;
                select.appendChild(option);
                const alternateOption = document.createElement("option");
                alternateOption.value = careerId;
                alternateOption.textContent = name;
                alternateSelect.appendChild(alternateOption);
            });
        } catch (error) {
            const option = document.createElement("option");
            option.disabled = true;
            option.textContent = "Career options could not be loaded";
            select.appendChild(option);
            const alternateOption = document.createElement("option");
            alternateOption.disabled = true;
            alternateOption.textContent = "Career options could not be loaded";
            alternateSelect.appendChild(alternateOption);
            console.error(error);
        }
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
        quizAnswers = {
            education: document.getElementById("education").value,
            country: document.getElementById("country").value,
            preferred_career: document.getElementById("preferred-career").value,
            subjects: selectedValues("subjects"),
            interests: selectedValues("interests"),
            skills: selectedValues("skills"),
            work_styles: selectedValues("work_styles"),
            asked_questions: [],
            follow_up_answers: []
        };
        if (!quizAnswers.country) {
            errorBox.textContent = "Please choose a country so the education guidance can be relevant.";
            errorBox.classList.remove("d-none");
            return;
        }
        feedbackSubmissionId = null;
        await refreshRecommendations(true);
    });

    async function refreshRecommendations(showPageError) {
        const submit = document.getElementById("quiz-submit");
        submit.disabled = true;
        submit.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Finding career ideas…';
        try {
            const response = await fetch("/api/v1/career-quiz", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(quizAnswers)
            });
            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.error || "Unable to generate your career ideas.");
            }
            recommendedIds = result.recommendations.map(function (item) { return item.id; });
            renderRecommendations(result.recommendations, result.recommendation_engine);
            renderFollowUpQuestion(result.follow_up_question);
            if (result.recommendations.length && result.recommendations[0].country_guidance) {
                const guidance = result.recommendations[0].country_guidance;
                countryGuidance.textContent = `${guidance.country} pathway overview: ${guidance.education_pathway} ${guidance.learning_opportunities} ${guidance.qualification_note}`;
                countryGuidance.classList.remove("d-none");
            } else {
                countryGuidance.classList.add("d-none");
            }
            renderFeedbackOptions(result.recommendations);
            feedbackMessage.textContent = "";
            feedbackSubmissionId = null;
            resultsSection.classList.remove("d-none");
            if (showPageError) {
                resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
            }
            return true;
        } catch (error) {
            errorBox.textContent = error.message || "Unable to generate recommendations. Please try again.";
            errorBox.classList.remove("d-none");
            return false;
        } finally {
            submit.disabled = false;
            submit.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-2"></i>Show my career ideas';
        }
    }

    function renderRecommendations(items, engine) {
        recommendations.replaceChildren();
        const engineNote = document.getElementById("recommendation-engine-note");
        engineNote.textContent = engine && engine.mode === "hybrid"
            ? "These suggestions combine the transparent rule-based match with a locally trained ranking signal from opted-in feedback. Model scores are not probabilities."
            : "These suggestions use transparent rule-based matching and your saved preferences, when available. They are exploration aids, not predictions.";
        if (engine && engine.notice) {
            engineNote.textContent += " " + engine.notice;
        }
        if (!items.length) {
            const message = document.createElement("p");
            message.className = "text-muted";
            message.textContent = "There is not enough matching information to recommend a career yet. Add a subject, interest, skill, or dream career and try again.";
            recommendations.appendChild(message);
            return;
        }
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
            score.setAttribute("aria-label", `Match score: ${item.match_percentage} percent`);
            header.prepend(nameBlock);
            card.appendChild(header);
            addText(card, "p", `Heuristic confidence: ${item.confidence || "limited"}; uncertainty ${item.uncertainty ?? 1}. This is not a probability.`, "small text-muted");
            addText(card, "h4", "Why it appeared", "h6 fw-bold");
            const reasons = document.createElement("ul");
            (item.reasons || []).forEach(function (reason) { addText(reasons, "li", reason); });
            card.appendChild(reasons);
            if (item.related_alternatives && item.related_alternatives.length) {
                addText(card, "h4", "Related alternatives to explore", "h6 fw-bold mt-3");
                addText(card, "p", item.related_alternatives.join(" · "), "small text-muted");
            }
            addText(card, "h4", "Skills to explore", "h6 fw-bold mt-3");
            addText(card, "p", (item.skill_gaps || item.suggested_skills || []).join(" · ") || "Your listed skills already cover the signals configured for this career.", "mb-3");
            const link = document.createElement("a");
            link.className = "btn btn-outline-primary btn-sm";
            link.href = `/career?id=${encodeURIComponent(item.id)}`;
            link.textContent = "Explore this roadmap";
            card.appendChild(link);
            column.appendChild(card);
            recommendations.appendChild(column);
        });
    }

    function renderFollowUpQuestion(question) {
        const choices = document.getElementById("follow-up-choices");
        choices.replaceChildren();
        if (!question) {
            followUpPanel.classList.add("d-none");
            return;
        }
        document.getElementById("follow-up-prompt").textContent = question.prompt;
        document.getElementById("follow-up-why").textContent = question.why;
        question.choices.forEach(function (choice) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "btn btn-outline-primary";
            button.textContent = choice.label;
            button.addEventListener("click", function () {
                answerFollowUp(question.id, choice.id);
            });
            choices.appendChild(button);
        });
        followUpPanel.dataset.questionId = question.id;
        followUpPanel.classList.remove("d-none");
    }

    async function answerFollowUp(questionId, choiceId) {
        if (!quizAnswers || quizAnswers.asked_questions.includes(questionId)) return;
        quizAnswers.asked_questions.push(questionId);
        const answer = choiceId ? {
            question_id: questionId,
            choice_id: choiceId
        } : null;
        if (answer) quizAnswers.follow_up_answers.push(answer);
        feedbackSubmissionId = null;
        const refreshed = await refreshRecommendations(false);
        if (!refreshed) {
            quizAnswers.asked_questions = quizAnswers.asked_questions.filter(
                function (id) { return id !== questionId; }
            );
            if (answer) {
                quizAnswers.follow_up_answers = quizAnswers.follow_up_answers.filter(
                    function (item) { return item !== answer; }
                );
            }
        }
    }

    document.getElementById("skip-follow-up").addEventListener("click", function () {
        const questionId = followUpPanel.dataset.questionId;
        if (questionId) answerFollowUp(questionId, null);
    });

    function renderFeedbackOptions(items) {
        const container = document.getElementById("career-feedback-options");
        container.replaceChildren();
        items.forEach(function (item) {
            const row = document.createElement("div");
            row.className = "d-flex flex-wrap justify-content-between align-items-center gap-2 border rounded-3 p-2";
            const name = addText(row, "span", item.name, "fw-semibold");
            name.id = `feedback-career-label-${item.id}`;
            const select = document.createElement("select");
            select.className = "form-select form-select-sm";
            select.dataset.careerId = item.id;
            select.setAttribute("aria-labelledby", name.id);
            [
                ["", "Choose reaction"],
                ["liked", "Interested"],
                ["rejected", "Not for me"],
            ].forEach(function (optionData) {
                const option = document.createElement("option");
                option.value = optionData[0];
                option.textContent = optionData[1];
                select.appendChild(option);
            });
            row.appendChild(select);
            container.appendChild(row);
        });
    }

    function setFeedbackMessage(message, showLoginLink) {
        feedbackMessage.replaceChildren();
        feedbackMessage.appendChild(document.createTextNode(message));
        if (showLoginLink) {
            feedbackMessage.appendChild(document.createTextNode(" "));
            const link = document.createElement("a");
            link.href = "/login";
            link.textContent = "Log in";
            feedbackMessage.appendChild(link);
            feedbackMessage.appendChild(document.createTextNode(" to save feedback."));
        }
    }

    feedbackForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        if (!feedbackForm.reportValidity()) return;
        const reactions = Array.from(
            document.querySelectorAll("#career-feedback-options select")
        );
        const likedCareerIds = [];
        const rejectedCareerIds = [];
        reactions.forEach(function (select) {
            if (select.value === "liked") likedCareerIds.push(Number(select.dataset.careerId));
            if (select.value === "rejected") rejectedCareerIds.push(Number(select.dataset.careerId));
        });
        const alternateValue = document.getElementById("feedback-alternate-career").value;
        const alternateCareerId = alternateValue ? Number(alternateValue) : null;
        if (!likedCareerIds.length && !rejectedCareerIds.length && alternateCareerId === null) {
            setFeedbackMessage("Select a reaction to at least one career, or choose another career.", false);
            return;
        }
        if (!feedbackSubmissionId) {
            if (!globalThis.crypto || typeof globalThis.crypto.randomUUID !== "function") {
                setFeedbackMessage("Secure feedback submission IDs are unavailable in this browser.", false);
                return;
            }
            feedbackSubmissionId = globalThis.crypto.randomUUID();
        }
        const submitButton = document.getElementById("submit-recommendation-feedback");
        submitButton.disabled = true;
        try {
            const response = await fetch("/api/v1/career-quiz/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    submission_id: feedbackSubmissionId,
                    answers: quizAnswers,
                    recommended_career_ids: recommendedIds.slice(0, 5),
                    liked_career_ids: likedCareerIds,
                    rejected_career_ids: rejectedCareerIds,
                    alternate_career_id: alternateCareerId,
                    overall_feedback: document.getElementById("overall-feedback").value,
                    reason: document.getElementById("feedback-reason").value,
                    preferred_work_styles: document.getElementById("feedback-work-style").value
                        ? [document.getElementById("feedback-work-style").value] : [],
                    priorities: document.getElementById("feedback-priority").value
                        ? [document.getElementById("feedback-priority").value] : [],
                    training_consent: document.getElementById("feedback-training-consent").checked
                })
            });
            const result = await response.json();
            if (!response.ok || !result.success) {
                setFeedbackMessage(
                    result.error || "Unable to save feedback.",
                    response.status === 401
                );
                return;
            }
            setFeedbackMessage(
                result.message + (result.stored_for_training
                    ? " Your optional training consent was recorded."
                    : " It will not be used for shared-model training."),
                false
            );
        } catch {
            setFeedbackMessage("Unable to reach CareerPath. Check your connection and try again.", false);
        } finally {
            submitButton.disabled = false;
        }
    });

    document.getElementById("withdraw-training-consent").addEventListener("click", async function () {
        if (!globalThis.confirm("Remove your previously opted-in feedback from future training datasets?")) return;
        const button = document.getElementById("withdraw-training-consent");
        button.disabled = true;
        try {
            const response = await fetch("/api/v1/career-quiz/feedback/training-consent", {
                method: "DELETE"
            });
            const result = await response.json();
            if (!response.ok || !result.success) {
                setFeedbackMessage(result.error || "Unable to withdraw training consent.", response.status === 401);
                return;
            }
            document.getElementById("feedback-training-consent").checked = false;
            setFeedbackMessage(result.message, false);
        } catch {
            setFeedbackMessage("Unable to reach CareerPath. Check your connection and try again.", false);
        } finally {
            button.disabled = false;
        }
    });

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

    loadCareerOptions();
})();
