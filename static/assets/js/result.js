document.addEventListener('DOMContentLoaded', function () {
    document.body.classList.add('mobile-nav-active');
    // Navigation between steps
    document.querySelectorAll(".btn-outline-primary").forEach(button => {
        button.addEventListener("click", function () {
            const stepNumber = this.getAttribute("step_number");
            navigateToStep(stepNumber);
        });
    });
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
