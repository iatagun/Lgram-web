function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    
    // Hide all tab content with animation
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    
    // Remove active class from all tab links
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    
    // Show the selected tab and add active class
    const targetTab = document.getElementById(tabName);
    if (targetTab) {
        targetTab.style.display = "block";
        targetTab.scrollIntoView({ behavior: 'smooth' });
    }
    if (evt && evt.currentTarget) {
        evt.currentTarget.className += " active";
    }
    
    // Handle specific tab initialization
    if (tabName === 'TransitionAnalysis') {
        initializeTransitionAnalysis();
    } else if (tabName === 'CoherenceReport') {
        initializeCoherenceReport();
    }
}

function initializeTransitionAnalysis() {
    console.log('Transition Analysis tab initialized - ready for future implementation');
}

function initializeCoherenceReport() {
    console.log('Coherence Report tab initialized - ready for future implementation');
}

function initializeAnalysisTools() {
    // Keep for compatibility
    console.log('Analysis tools compatibility function');
}

function loadTransitionAnalysisContent() {
    // This function is kept for compatibility but content is now inline
    console.log('Transition analysis loaded inline');
}

function loadCoherenceReportContent() {
    // This function is kept for compatibility but content is now inline
    console.log('Coherence report loaded inline');
}

// Update slider value display
function updateSliderValue(elementId, value) {
    document.getElementById(elementId).textContent = value;
}

// Load more history items via AJAX
let historyOffset = 3; // Start after initial 3 items

function loadMoreHistory() {
    const btn = document.getElementById('show-more-btn');
    const spinner = document.getElementById('load-more-spinner');
    const container = document.getElementById('show-more-container');
    
    // Show loading state
    btn.disabled = true;
    spinner.classList.remove('d-none');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
    
    // Make AJAX request
    fetch(`/api/load-more-history/?offset=${historyOffset}&limit=5`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add new history items
                data.history_items.forEach(item => {
                    const historyItem = createHistoryItemElement(item);
                    container.parentNode.insertBefore(historyItem, container);
                });
                
                historyOffset += data.loaded_count;
                
                // Update or hide the "Show More" button
                if (data.has_more) {
                    const remaining = data.total_count - historyOffset;
                    btn.innerHTML = `<i class="fas fa-plus-circle me-2"></i>Show More History <span class="badge bg-primary ms-2">${remaining} more</span>`;
                    btn.disabled = false;
                } else {
                    container.style.display = 'none';
                }
                
                // Add animation to new items
                const newItems = container.parentNode.querySelectorAll('.history-item:not(.animated)');
                newItems.forEach((item, index) => {
                    item.classList.add('animated');
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    
                    setTimeout(() => {
                        item.style.transition = 'all 0.4s ease-out';
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                    }, index * 100);
                });
                
                showAlert(`Loaded ${data.loaded_count} more history items`, 'success');
            } else {
                showAlert('Failed to load more history: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Error loading more history:', error);
            showAlert('Failed to load more history', 'danger');
            btn.innerHTML = '<i class="fas fa-plus-circle me-2"></i>Show More History';
            btn.disabled = false;
        })
        .finally(() => {
            spinner.classList.add('d-none');
        });
}

function createHistoryItemElement(item) {
    const div = document.createElement('div');
    div.className = 'history-item mb-3';
    
    // Determine model badge class
    const badgeClass = item.model_type === 'centering' ? 'bg-info' : 'bg-secondary';
    
    div.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-3">
            <div class="d-flex gap-2">
                <span class="badge ${badgeClass}">${item.model_name}</span>
                <span class="badge bg-success">Completed</span>
            </div>
            <button type="button" class="btn btn-primary btn-sm" onclick="copyText('${item.generated_text.replace(/'/g, "\\'")}', this)">
                <i class="fas fa-copy me-1"></i>Copy
            </button>
        </div>
        
        <div class="mb-3">
            <h6 class="text-muted mb-2">
                <i class="fas fa-keyboard me-1"></i>Input Text:
            </h6>
            <div class="input-display p-2 bg-light rounded">
                ${item.input_text || "No input provided"}
            </div>
        </div>
        
        <div class="mb-2">
            <h6 class="text-muted mb-2">
                <i class="fas fa-robot me-1"></i>Generated Output:
            </h6>
            <div class="output-display p-3 bg-white rounded border">
                ${item.generated_text}
            </div>
        </div>
        
        <div class="text-end">
            <small class="text-muted">
                <i class="fas fa-clock me-1"></i>
                Generated on ${item.created_at}
            </small>
        </div>
    `;
    
    return div;
}

// Initialize tabs when DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
    // Click the default tab
    document.getElementById("defaultOpen").click();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize tooltips and animations
    initInteractiveElements();
});

// Form validation and submission
function submitForm() {
    console.log('submitForm() called'); // Debug log
    
    const input = document.getElementById('input_text');
    const submitBtn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');
    
    console.log('Input value:', input ? input.value : 'Input element not found'); // Debug log
    
    // Validate input - more flexible validation
    if (!input || !input.value.trim()) {
        console.log('Validation failed: Empty input'); // Debug log
        showAlert('Please enter some text.', 'warning');
        if (input) input.focus();
        return false;
    }
    
    // Minimum 2 characters should be enough
    if (input.value.trim().length < 2) {
        console.log('Validation failed: Text too short'); // Debug log
        showAlert('Please enter at least 2 characters.', 'warning');
        input.focus();
        return false;
    }
    
    console.log('Validation passed, submitting form'); // Debug log
    
    // Show loading state - only in one place
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
    }
    
    if (loading) {
        loading.style.display = 'block';
    }
    
    // Add visual feedback
    if (input) {
        input.style.borderColor = '#28a745';
    }
    
    console.log('Form submitted successfully'); // Debug log
    return true;
}

// Enhanced copy function with better feedback
function copyText(text, button) {
    navigator.clipboard.writeText(text).then(function() {
        const originalText = button.innerHTML;
        const originalClass = button.className;
        
        // Success feedback
        button.innerHTML = '✓ Copied!';
        button.className = button.className.replace('btn-primary', 'btn-success');
        
        // Add success animation
        button.style.transform = 'scale(1.1)';
        
        setTimeout(function() {
            button.innerHTML = originalText;
            button.className = originalClass;
            button.style.transform = 'scale(1)';
        }, 2000);
        
        // Show success message
        showAlert('Text copied!', 'success');
        
    }).catch(function(err) {
        console.error('Copy error: ', err);
        showAlert('Copy failed!', 'danger');
    });
}

// Enhanced clear history function
function clearHistory() {
    if (confirm('Are you sure you want to delete all history?\n\nThis action cannot be undone.')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.style.display = 'none';
        
        // Add CSRF token
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Add clear history flag
        const clearInput = document.createElement('input');
        clearInput.type = 'hidden';
        clearInput.name = 'clear_history';
        clearInput.value = '1';
        
        form.appendChild(csrfInput);
        form.appendChild(clearInput);
        document.body.appendChild(form);
        
        // Add loading state before submit
        const clearBtn = document.querySelector('.btn-danger');
        if (clearBtn) {
            clearBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Deleting...';
            clearBtn.disabled = true;
        }
        
        form.submit();
    }
}

// Show alert messages
function showAlert(message, type = 'info') {
    // Create alert element if it doesn't exist
    let alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alertContainer';
        alertContainer.style.position = 'fixed';
        alertContainer.style.top = '20px';
        alertContainer.style.right = '20px';
        alertContainer.style.zIndex = '9999';
        alertContainer.style.maxWidth = '400px';
        document.body.appendChild(alertContainer);
    }
    
    // Create alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.style.marginBottom = '10px';
    alert.innerHTML = `
        <strong>${message}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto remove after 3 seconds
    setTimeout(function() {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 3000);
}

// Initialize form validation
function initFormValidation() {
    const textarea = document.getElementById('input_text');
    const numSentences = document.getElementById('num_sentences');
    const length = document.getElementById('length');
    
    if (textarea) {
        // Character counter
        textarea.addEventListener('input', function() {
            const count = this.value.length;
            const maxLength = 1000; // Set a reasonable limit
            
            // Update counter (create if doesn't exist)
            let counter = document.getElementById('charCounter');
            if (!counter) {
                counter = document.createElement('small');
                counter.id = 'charCounter';
                counter.className = 'text-muted';
                textarea.parentNode.appendChild(counter);
            }
            
            counter.textContent = `${count}/${maxLength} characters`;
            
            // Color coding
            if (count > maxLength * 0.9) {
                counter.style.color = '#dc3545';
            } else if (count > maxLength * 0.7) {
                counter.style.color = '#ffc107';
            } else {
                counter.style.color = '#6c757d';
            }
        });
    }
    
    // Validate number inputs
    if (numSentences) {
        numSentences.addEventListener('change', function() {
            if (this.value < 1) this.value = 1;
            if (this.value > 10) this.value = 10;
        });
    }
    
    if (length) {
        length.addEventListener('change', function() {
            if (this.value < 5) this.value = 5;
            if (this.value > 30) this.value = 30;
        });
    }
}

// Initialize interactive elements
function initInteractiveElements() {
    // Add hover effects to history items
    const historyItems = document.querySelectorAll('.history-item');
    historyItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(8px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
    
    // Add focus effects to form controls
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentNode.style.transform = 'scale(1.02)';
        });
        
        control.addEventListener('blur', function() {
            this.parentNode.style.transform = 'scale(1)';
        });
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to submit form
    if (e.ctrlKey && e.key === 'Enter') {
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.click();
        }
    }
    
    // Tab navigation between tabs
    if (e.ctrlKey && e.key === '1') {
        e.preventDefault();
        document.getElementById('defaultOpen').click();
    }
    
    if (e.ctrlKey && e.key === '2') {
        e.preventDefault();
        const historyBtn = document.querySelector('.tablinks:nth-child(2)');
        if (historyBtn) historyBtn.click();
    }
});

// Auto-save draft to localStorage
function autoSaveDraft() {
    const textarea = document.getElementById('input_text');
    if (textarea) {
        textarea.addEventListener('input', function() {
            localStorage.setItem('lgram_draft', this.value);
        });
        
        // Load saved draft on page load
        const savedDraft = localStorage.getItem('lgram_draft');
        if (savedDraft && !textarea.value) {
            textarea.value = savedDraft;
        }
    }
}

// Initialize auto-save
document.addEventListener('DOMContentLoaded', autoSaveDraft);
