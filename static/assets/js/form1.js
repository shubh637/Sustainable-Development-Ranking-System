$(document).ready(function() {
    // Navigation between steps
    $(".btn-navigate-form-step").on("click", function(e) {
        const stepNumber = $(this).attr("step_number");
        navigateToStep(stepNumber);
    });
    
    // Recalculate button
    $("#recalculate-btn").on("click", function() {
        $("#carbonCalculatorForm").show();
        navigateToStep(1);
    });
    
    function navigateToStep(stepNumber) {
        // Hide all steps
        $(".form-step").removeClass("active");
        
        // Show current step
        $(`#step-${stepNumber}`).addClass("active");
        
        // Update progress steps
        $(".form-stepper-list").removeClass("form-stepper-active");
        $(`.form-stepper-list[step="${stepNumber}"]`).addClass("form-stepper-active");
        
        // For steps before current, mark as complete
        for (let i = 1; i < stepNumber; i++) {
            $(`.form-stepper-list[step="${i}"] .form-stepper-circle`).html('<i class="bi bi-check"></i>');
        }
        
        // For steps after current, reset numbers
        for (let i = stepNumber + 1; i <= 4; i++) {
            $(`.form-stepper-list[step="${i}"] .form-stepper-circle`).html(`<span>${i}</span>`);
        }
    }
});