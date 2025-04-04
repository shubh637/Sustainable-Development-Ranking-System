document.addEventListener('DOMContentLoaded', function () {
    // Form submission handler
    // document.getElementById("sustainabilityForm").addEventListener("submit", function (e) {
    //     e.preventDefault();

    //     let formData = new FormData(this);

    //     fetch("", {
    //         method: "POST",
    //         body: formData,
    //         headers: {
    //             'X-Requested-With': 'XMLHttpRequest' // Identify as AJAX request
    //         }
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //         // Update results with server data
    //         document.getElementById("score").textContent = data.sustainability_score;
    //         document.getElementById("roi").textContent = data.roi + "%";
    //         document.getElementById("benef").textContent = data.cost_benefit.toFixed(1) + "x";

    //         // Show results
    //         document.getElementById("sustainabilityForm").style.display = "none";
    //         document.getElementById("results").style.display = "block";

    //         // Scroll to results
    //         document.getElementById("results").scrollIntoView({ behavior: 'smooth', block: 'start' });
    //     })
    //     .catch(error => console.error("Error:", error));
    // });

    // Navigation between steps
    document.querySelectorAll(".btn-outline-primary").forEach(button => {
        button.addEventListener("click", function () {
            const stepNumber = this.getAttribute("step_number");
            navigateToStep(stepNumber);
        });
    });

    // Calculate button (submits the form)
    // document.getElementById("calculate-btn").addEventListener("click", function () {
    //     document.getElementById("sustainabilityForm").dispatchEvent(new Event('submit'));
    // });

    // Recalculate button
    document.getElementById("recalculate-btn").addEventListener("click", function () {
        // document.getElementById("results").style.display = "none";
        // document.getElementById("sustainabilityForm").style.display = "block";
        navigateToStep(1);
    });

    function navigateToStep(stepNumber) {
        // Hide all steps
        document.querySelectorAll(".form-step").forEach(step => {
            step.classList.remove("active");
        });

        // Show current step
        document.getElementById(`step-${stepNumber}`).classList.add("active");

        // Update progress steps
        document.querySelectorAll(".form-stepper-list").forEach(step => {
            step.classList.remove("form-stepper-active");
        });
        document.querySelector(`.form-stepper-list[step="${stepNumber}"]`).classList.add("form-stepper-active");

        // Mark steps before current as complete
        for (let i = 1; i < stepNumber; i++) {
            const circle = document.querySelector(`.form-stepper-list[step="${i}"] .form-stepper-circle`);
            if (circle) circle.innerHTML = '<span>✓</span>';
        }

        // Reset numbers for steps after the current one
        for (let i = parseInt(stepNumber) + 1; i <= 6; i++) {
            const circle = document.querySelector(`.form-stepper-list[step="${i}"] .form-stepper-circle`);
            if (circle) circle.innerHTML = `<span>${i}</span>`;
        }
    }
});
